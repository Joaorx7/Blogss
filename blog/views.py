from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count
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
from .models import Post, Comentario, Categoria, Notificacao
from .forms import CadastroForm
import markdown
import random
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
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
    seguindo = perfil.seguindo.all()
    posts = Post.objects.filter(autor=usuario).order_by('-criado_em')

    # Garantir que sempre haja uma foto
    foto_url = perfil.foto.url if perfil.foto else '/media/img_resto/Account.png'

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'seguidores': seguidores,
        'seguindo': seguindo,
        'posts': posts,
        'foto_url': foto_url,
    }
    return render(request, 'blog/perfil_usuario.html', context)

@login_required
def remover_foto_perfil(request):
    usuario = request.user
    usuario.perfil.foto = None  # Remove a foto de perfil
    usuario.perfil.save()
    return redirect('perfil_usuario', username=usuario.username)

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

    # Pega os usuários que o user atual está seguindo
    seguindo = User.objects.filter(perfil__seguidores=request.user)

    # Filtra os posts dos autores que o usuário segue
    posts = Post.objects.filter(autor__in=seguindo).order_by('-criado_em')

    return render(request, 'blog/feed.html', {'posts': posts})

from django.shortcuts import render
from .models import Post


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import markdown
from .models import Post, Comentario, Notificacao
from .forms import ComentarioForm
from .models import Categoria

def detalhes_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorias = Categoria.objects.all()
    
    # Comentários principais (sem pai)
    comentarios = Comentario.objects.filter(post=post, resposta_a__isnull=True).order_by('-criado_em')

    # Markdown do conteúdo do post
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
                    comentario.resposta_a = Comentario.objects.get(id=resposta_a_id)

                comentario.save()

                # Cria notificação para o autor do post
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


def sobre(request):
    return render(request, 'blog/sobre.html')

@require_POST
@login_required
def curtir_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.curtidas.all():
        post.curtidas.remove(user)
        curtido = False

        # Deleta a notificação de curtida se ela existir
        Notificacao.objects.filter(
            usuario=post.autor,
            texto__icontains=f"{user.username} curtiu seu post",
            link=f"/post/{post.id}/"
        ).delete()

    else:
        post.curtidas.add(user)
        curtido = True

        # Cria notificação apenas se não existir ainda
        if post.autor != user and not Notificacao.objects.filter(
            usuario=post.autor,
            texto__icontains=f"{user.username} curtiu seu post",
            link=f"/post/{post.id}/"
        ).exists():
            Notificacao.objects.create(
                usuario=post.autor,
                texto=f"{user.username} curtiu seu post: {post.titulo}",
                link=f"/post/{post.id}/"
            )

    return JsonResponse({
        'curtido': curtido,
        'total_curtidas': post.curtidas.count()
    })

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Post, Categoria, Perfil

from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Post, Categoria, Perfil  # Ajuste se o import for diferente

from django.core.paginator import Paginator
from django.db.models import Count

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render

def home(request):
    categoria_id = request.GET.get('categoria')
    ordenar = request.GET.get('ordenar', 'recentes')
    page = request.GET.get('page', 1)

    posts = Post.objects.all()

    if categoria_id:
        posts = posts.filter(categoria__id=categoria_id)

    if ordenar == 'curtidos':
        posts = posts.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas', '-criado_em')
    else:
        posts = posts.order_by('-criado_em')

    pagina = posts  # sem paginação

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        posts_html = ''
        for post in pagina:
            posts_html += render(request, 'blog/post_resumo.html', {'post': post}).content.decode('utf-8')

        return JsonResponse({
            'posts_html': posts_html,
            'tem_mais': False  # sem paginação
        })

    return render(request, 'blog/home.html', {
        'posts': pagina,
        'categoria_id': int(categoria_id) if categoria_id else None,
        'ordenar': ordenar,
    })


def posts_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    posts = Post.objects.filter(categoria=categoria).order_by('-criado_em')

    return render(request, 'blog/posts_por_categoria.html', {
        'posts': posts,
        'categoria': categoria,
        # Não precisa passar 'categorias_principais' aqui!
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
def deixar_de_seguir(request, username):
    usuario_para_parar = get_object_or_404(User, username=username)
    if usuario_para_parar != request.user:
        usuario_para_parar.perfil.seguidores.remove(request.user)
    return redirect('perfil_usuario', username=username)

@login_required
@require_POST
def seguir_ou_nao(request, username):
    usuario_logado = request.user
    perfil = usuario_logado.perfil
    alvo = get_object_or_404(User, username=username)
    perfil_alvo = alvo.perfil

    if usuario_logado in perfil_alvo.seguidores.all():
        perfil_alvo.seguidores.remove(usuario_logado)
        seguindo = False
    else:
        perfil_alvo.seguidores.add(usuario_logado)
        seguindo = True

    return JsonResponse({'seguindo': seguindo, 'total_seguidores': perfil_alvo.seguidores.count()})


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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def editar_perfil(request):
    perfil = request.user.perfil

    if request.method == 'POST':
        bio = request.POST.get('bio')
        foto = request.FILES.get('foto')
        remover_foto = request.POST.get('remover_foto')  # verifica se a opção foi marcada

        perfil.bio = bio

        if remover_foto:
            if perfil.foto:
                perfil.foto.delete(save=False)  # remove a foto do sistema de arquivos
                perfil.foto = None
        elif foto:
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
    notificacoes_nao_lidas = Notificacao.objects.filter(usuario=user, lida=False).count()

    context = {
        'total_posts': total_posts,
        'total_comentarios': total_comentarios,
        'total_curtidas': total_curtidas,
        'seguidores': seguidores,
        'seguindo': seguindo,
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

class UsernamePasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_username_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/redefinir/enviado/'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            form = PasswordResetForm({'email': user.email})
            if form.is_valid():
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    from_email=None,
                    email_template_name=self.email_template_name,
                    subject_template_name=self.subject_template_name,
                )
                messages.success(request, 'Um e-mail de redefinição foi enviado.')
                return redirect(self.success_url)
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

        return render(request, self.template_name)
    
from django.contrib.auth.views import PasswordResetDoneView

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'