from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PostForm
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .forms import ComentarioForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from blog.models import Perfil
from .models import Post, Comentario, Categoria, Mensagem, Notificacao
from .forms import MensagemForm, CadastroForm
import markdown
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import render
from django.contrib.messages import get_messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from .forms import CustomUserCreationForm

def buscar_usuarios(request):
    termo = request.GET.get('q', '')
    usuarios = User.objects.filter(username__icontains=termo)
    return render(request, 'blog/buscar_usuarios.html', {
        'usuarios': usuarios,
        'termo': termo
    })

def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil = usuario.perfil
    seguidores = perfil.seguidores.all()
    seguindo = usuario.seguindo.all()
    posts = Post.objects.filter(autor=usuario)

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'seguidores': seguidores,
        'seguindo': seguindo,
        'posts': posts,
    }
    return render(request, 'blog/perfil_usuario.html', context)

@login_required
def novo_post(request):
    categorias = Categoria.objects.all()  # ← Adicionado aqui

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # ← request.FILES já está ok
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'blog/novo_post.html', {'form': form, 'categorias': categorias})

def feed_personalizado(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Garante que o usuário tenha um perfil
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    seguindo = perfil.seguidores.all()
    posts = Post.objects.filter(autor__in=seguindo).order_by('-criado_em')

    return render(request, 'blog/feed.html', {'posts': posts})

from django.shortcuts import render
from .models import Post

def home(request):
    categoria = request.GET.get('categoria')
    ordenar = request.GET.get('ordenar')

    posts = Post.objects.all()

    if categoria:
        posts = posts.filter(categorias__nome=categoria)

    if ordenar == 'likes':
        posts = posts.annotate(num_likes=Count('curtidas')).order_by('-num_likes')
    else:
        posts = posts.order_by('-data_publicacao')

    return render(request, 'blog/home.html', {'posts': posts})
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import markdown
from .models import Post, Comentario, Notificacao
from .forms import ComentarioForm
from .models import Categoria

def detalhes_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comentarios = post.comentarios.filter(resposta_a__isnull=True).order_by('-criado_em')
    categorias = Categoria.objects.all()

    # Markdown
    post_conteudo_html = markdown.markdown(post.conteudo)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ComentarioForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.post = post
                comentario.autor = request.user

                # Verifica se é resposta a outro comentário
                resposta_a_id = request.POST.get('resposta_a')
                if resposta_a_id:
                    try:
                        comentario.resposta_a = Comentario.objects.get(id=resposta_a_id)
                    except Comentario.DoesNotExist:
                        pass  # ignora se o comentário pai não existir

                comentario.save()

                # Notifica o autor do post
                if post.autor != request.user:
                    Notificacao.objects.create(
                        usuario=post.autor,
                        texto=f'{request.user.username} comentou no seu post "{post.titulo}".',
                        link=reverse('detalhes_post', args=[post.id])
                    )

                return redirect('detalhes_post', post_id=post.id)
        else:
            return redirect('login')
    else:
        form = ComentarioForm()

    return render(request, 'blog/detalhes_post.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'categorias': categorias,
        'post_conteudo_html': post_conteudo_html,
    })


def cadastro(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'blog/cadastro.html', {'form': form, 'categorias': categorias})

def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorias = Categoria.objects.all()

    if post.autor != request.user:
        messages.error(request, 'Você não tem permissão para editar este post.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  # ← Adicionado request.FILES aqui
        if form.is_valid():
            form.save()
            return redirect('detalhes_post', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/editar_post.html', {'form': form, 'categorias': categorias})

@login_required
def deletar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorias = Categoria.objects.all()

    if post.autor != request.user:
        messages.error(request, 'Você não tem permissão para excluir este post.')
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'blog/deletar_post.html', {'post': post, 'categorias': categorias})

@login_required
def sair(request):
    logout(request)
    return redirect('home')

def posts_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    posts = Post.objects.filter(categoria=categoria).order_by('-criado_em')
    categorias = Categoria.objects.all()

    return render(request, 'blog/posts_por_categoria.html', {
        'posts': posts,
        'categoria': categoria,
        'categorias': categorias
    })

def sobre(request):
    return render(request, 'blog/sobre.html')

@require_POST
@login_required
def curtir_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.curtidas.all():
        post.curtidas.remove(request.user)
        curtido = False
    else:
        post.curtidas.add(request.user)
        curtido = True

    return JsonResponse({
        'curtido': curtido,
        'total_curtidas': post.curtidas.count()
    })

def home(request):
    termo_busca = request.GET.get('q', '')

    if termo_busca:
        posts_lista = Post.objects.filter(
            titulo__icontains=termo_busca
        ) | Post.objects.filter(
            conteudo__icontains=termo_busca
        )
    else:
        posts_lista = Post.objects.all()

    posts_lista = posts_lista.order_by('-criado_em')
    paginator = Paginator(posts_lista, 5)
    pagina = request.GET.get('page')
    posts = paginator.get_page(pagina)

    return render(request, 'blog/home.html', {
        'posts': posts,
        'termo_busca': termo_busca
    })

@login_required
def seguir_usuario(request, username):
    usuario_para_seguir = get_object_or_404(User, username=username)

    if usuario_para_seguir != request.user:
        perfil_alvo = usuario_para_seguir.perfil
        perfil_alvo.seguidores.add(request.user)

        # Criar notificação
        Notificacao.objects.create(
            usuario=usuario_para_seguir,
            texto=f'{request.user.username} começou a te seguir!'
        )

    return redirect('perfil_usuario', username=username)
@login_required
def deixar_de_seguir_usuario(request, username):
    usuario_para_parar = get_object_or_404(User, username=username)
    if usuario_para_parar != request.user:
        usuario_para_parar.perfil.seguidores.remove(request.user)
    return redirect('perfil_usuario', username=username)

@login_required
def caixa_entrada(request):
    mensagens = request.user.mensagens_recebidas.order_by('-enviada_em')
    return render(request, 'blog/caixa_entrada.html', {'mensagens': mensagens})

@login_required
def enviar_mensagem(request, username):
    destinatario = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.remetente = request.user
            mensagem.destinatario = destinatario
            mensagem.save()
            return redirect('perfil_usuario', username=username)
    else:
        form = MensagemForm()
    return render(request, 'blog/enviar_mensagem.html', {'form': form, 'destinatario': destinatario})

@login_required
def caixa_de_entrada(request):
    mensagens = Mensagem.objects.filter(destinatario=request.user).order_by('-enviada_em')
    return render(request, 'blog/caixa_de_entrada.html', {'mensagens': mensagens})

@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)

    if request.method == 'POST':
        form = ComentarioForm(request.POST, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentário editado com sucesso!')
            return redirect('detalhes_post', post_id=comentario.post.id)
    else:
        form = ComentarioForm(instance=comentario)

    return render(request, 'blog/editar_comentario.html', {
        'form': form,
        'comentario': comentario
    })


@login_required
def deletar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)

    if request.method == 'POST':
        comentario.delete()
        messages.success(request, 'Comentário excluído com sucesso!')
        return redirect('detalhes_post', post_id=comentario.post.id)

    return render(request, 'blog/deletar_comentario.html', {
        'comentario': comentario
    })

def ver_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comentarios = Comentario.objects.filter(post=post).order_by('-criado_em')
    form = ComentarioForm()

    # Converte Markdown para HTML
    post_conteudo_html = markdown.markdown(post.conteudo)

    context = {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'post_conteudo_html': post_conteudo_html,
    }
    return render(request, 'blog/ver_post.html', context)

@login_required
def editar_perfil(request):
    perfil = request.user.perfil

    if request.method == 'POST':
        bio = request.POST.get('bio')
        foto = request.FILES.get('foto')

        perfil.bio = bio
        if foto:
            perfil.foto = foto
        perfil.save()

        return redirect('perfil_usuario', username=request.user.username)

    return render(request, 'blog/editar_perfil.html', {'perfil': perfil})

@login_required
def notificacoes(request):
    notificacoes = request.user.notificacoes.order_by('-criada_em')

    # Marca todas como lidas
    notificacoes.update(lida=True)

    return render(request, 'blog/notificacoes.html', {'notificacoes': notificacoes})

@login_required
def deletar_notificacao(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.delete()
    return redirect('notificacoes')

@login_required
def estatisticas_usuario(request):
    user = request.user
    perfil = user.perfil

    total_posts = Post.objects.filter(autor=user).count()
    total_comentarios = Comentario.objects.filter(autor=user).count()
    total_curtidas = Post.objects.filter(autor=user).aggregate(soma=Count('curtidas'))['soma'] or 0
    seguidores = perfil.seguidores.count()
    seguindo = user.seguindo.count()
    mensagens_enviadas = Mensagem.objects.filter(remetente=user).count()
    mensagens_recebidas = Mensagem.objects.filter(destinatario=user).count()
    notificacoes_nao_lidas = Notificacao.objects.filter(usuario=user, lida=False).count()

    context = {
        'total_posts': total_posts,
        'total_comentarios': total_comentarios,
        'total_curtidas': total_curtidas,
        'seguidores': seguidores,
        'seguindo': seguindo,
        'mensagens_enviadas': mensagens_enviadas,
        'mensagens_recebidas': mensagens_recebidas,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
    }

    return render(request, 'blog/estatisticas.html', context)



class PasswordResetViewDev(PasswordResetView):
    template_name = 'blog/password_reset_form.html'  # alterado para evitar pasta registration
    email_template_name = 'registration/password_reset_email.html'  # pode deixar assim se esse já existir
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('mostrar_link_reset')

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        users = User.objects.filter(email=email)
        if users.exists():
            user = users.first()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = self.request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )
            self.request.session["reset_link"] = reset_link
        return super().form_valid(form)

def mostrar_link_reset(request):
    reset_link = request.session.get("reset_link")
    if not reset_link:
        reset_link = "Link de redefinição não disponível."
    return render(request, 'blog/link_reset_mostrado.html', {'reset_link': reset_link})

def cadastro(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "blog/cadastro.html", {"form": form})


def termos_uso(request):
    return render(request, 'blog/termos_uso.html')