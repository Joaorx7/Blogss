# -------------------- BIBLIOTECAS E IMPORTAÇÕES --------------------

# Bibliotecas padrão
import random
import markdown

# Django - Autenticação e Usuários
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
)
from django.contrib.messages import get_messages

# Django - Atalhos e mensagens
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Django - HTTP, URLs e Views
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView

# Django - Templates e codificação
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# Django - Banco de dados
from django.db.models import Count, Q, Sum

# Django - Paginação
from django.core.paginator import Paginator

# Formularios personalizados
from .forms import (
    PostForm,
    ComentarioForm,
    CadastroForm,
    CustomUserCreationForm,
)

# Modelos personalizados
from .models import (
    Post,
    Comentario,
    Categoria,
    Notificacao,
    Perfil,
)

# Usuário customizado (caso esteja usando)
from django.contrib.auth import get_user_model
from PIL import Image
# -------------------- VIEWS --------------------

#Contém as funções e classes responsáveis por processar requisições e retornar respostas HTML ou JSON. É onde a lógica das páginas fica.


# Busca usuários pelo nome de usuário
@login_required
def buscar_usuarios(request):
    termo = request.GET.get('q', '')
    usuarios = User.objects.filter(username__icontains=termo)
    return render(request, 'blog/buscar_usuarios.html', {
        'usuarios': usuarios,
        'termo': termo
    })

# Exibe o perfil de um usuário
def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil = usuario.perfil
    seguidores = perfil.seguidores.all()
    seguindo = perfil.seguindo.all()
    posts = Post.objects.filter(autor=usuario).order_by('-criado_em')
    
    # Define imagem padrão se o usuário não tiver foto
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

# Remove a foto de perfil do usuário logado
@login_required
def remover_foto_perfil(request):
    usuario = request.user
    usuario.perfil.foto = None  
    usuario.perfil.save()
    return redirect('perfil_usuario', username=usuario.username)

# Cria um novo post
@login_required
def novo_post(request):
    categorias = Categoria.objects.all()  

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'blog/novo_post.html', {'form': form, 'categorias': categorias})

# Feed personalizado com base nos usuários seguidos
def feed_personalizado(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Garante que o perfil exista
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    # Busca usuários que o atual está seguindo
    seguindo = User.objects.filter(perfil__seguidores=request.user)

    # Mostra posts desses usuários
    posts = Post.objects.filter(autor__in=seguindo).order_by('-criado_em')

    return render(request, 'blog/feed.html', {'posts': posts})

# Exibe os detalhes de um post e permite comentarios
def detalhes_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorias = Categoria.objects.all()

    # Comentários que não são respostas (topo da thread)
    comentarios = Comentario.objects.filter(post=post, resposta_a__isnull=True).order_by('-criado_em')

    # Converte o conteúdo do post para HTML usando markdown
    post_conteudo_html = markdown.markdown(post.conteudo)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ComentarioForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.post = post
                comentario.autor = request.user

                # Caso o comentário seja resposta a outro
                resposta_a_id = request.POST.get('resposta_a')
                if resposta_a_id:
                    comentario.resposta_a = Comentario.objects.get(id=resposta_a_id)

                comentario.save()

                # Cria notificação se não for o próprio autor
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

# Cadastro de novo usuário
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

# Edição de um post existente
def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categorias = Categoria.objects.all()

    if post.autor != request.user:
        messages.error(request, 'Você não tem permissão para editar este post.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  
        if form.is_valid():
            form.save()
            return redirect('detalhes_post', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/editar_post.html', {'form': form, 'categorias': categorias})

# Deleta um post
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

# Logout do sistema
@login_required
def sair(request):
    logout(request)
    return redirect('home')

# Página estática "Sobre"
def sobre(request):
    return render(request, 'blog/sobre.html')

# Curtir e descurtir posts (via AJAX)
@require_POST
@login_required
def curtir_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.curtidas.all():
        # Se já curtiu, remove
        post.curtidas.remove(user)
        curtido = False

        # Remove notificação se existir
        Notificacao.objects.filter(
            usuario=post.autor,
            texto__icontains=f"{user.username} curtiu seu post",
            link=f"/post/{post.id}/"
        ).delete()
    else:
        # Adiciona curtida
        post.curtidas.add(user)
        curtido = True

        # Cria notificação se ainda não existir
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
@login_required
def home(request):
    # Captura filtros da URL: categoria, ordenação e paginação
    categoria_id = request.GET.get('categoria')
    ordenar = request.GET.get('ordenar', 'recentes')
    page = request.GET.get('page', 1)

    posts = Post.objects.all()

    # Filtra por categoria, se for passada
    if categoria_id:
        posts = posts.filter(categoria__id=categoria_id)

    # Ordena por número de curtidas ou por data de criação
    if ordenar == 'curtidos':
        posts = posts.annotate(num_curtidas=Count('curtidas')).order_by('-num_curtidas', '-criado_em')
    else:
        posts = posts.order_by('-criado_em')

    pagina = posts  # Aqui poderia ter paginação

    # AJAX: se for requisição JavaScript, retorna os posts como HTML
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        posts_html = ''
        for post in pagina:
            posts_html += render(request, 'blog/post_resumo.html', {'post': post}).content.decode('utf-8')

        return JsonResponse({
            'posts_html': posts_html,
            'tem_mais': False  # Aqui poderia ser dinâmico com paginação
        })

    return render(request, 'blog/home.html', {
        'posts': pagina,
        'categoria_id': int(categoria_id) if categoria_id else None,
        'ordenar': ordenar,
    })


def posts_por_categoria(request, categoria_id):
    # Lista posts de uma categoria específica
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    posts = Post.objects.filter(categoria=categoria).order_by('-criado_em')

    return render(request, 'blog/posts_por_categoria.html', {
        'posts': posts,
        'categoria': categoria,
    })


@login_required
def seguir_usuario(request, username):
    # Seguir um usuário e criar notificação
    usuario_para_seguir = get_object_or_404(User, username=username)

    if usuario_para_seguir != request.user:
        perfil_alvo = usuario_para_seguir.perfil
        perfil_alvo.seguidores.add(request.user)

        Notificacao.objects.create(
            usuario=usuario_para_seguir,
            texto=f'{request.user.username} começou a te seguir!'
        )

    return redirect('perfil_usuario', username=username)


@login_required
def deixar_de_seguir(request, username):
    # Deixar de seguir um usuário
    usuario_para_parar = get_object_or_404(User, username=username)
    if usuario_para_parar != request.user:
        usuario_para_parar.perfil.seguidores.remove(request.user)
    return redirect('perfil_usuario', username=username)


@login_required
@require_POST
def seguir_ou_nao(request, username):
    # Alterna entre seguir e deixar de seguir (usado via AJAX)
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
    # Permite ao autor editar o próprio comentário
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
    # Permite ao autor deletar seu comentário
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)

    if request.method == 'POST':
        comentario.delete()
        messages.success(request, 'Comentário excluído com sucesso!')
        return redirect('detalhes_post', post_id=comentario.post.id)

    return render(request, 'blog/deletar_comentario.html', {
        'comentario': comentario
    })


def ver_post(request, post_id):
    # Visualização de post com comentários e formulário
    post = get_object_or_404(Post, id=post_id)
    comentarios = Comentario.objects.filter(post=post).order_by('-criado_em')
    form = ComentarioForm()

    # Renderiza o conteúdo com markdown
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
    # Permite editar bio e foto do perfil (com crop para 1:1)
    perfil = request.user.perfil

    if request.method == 'POST':
        bio = request.POST.get('bio')
        foto = request.FILES.get('foto')
        remover_foto = request.POST.get('remover_foto')

        perfil.bio = bio

        if remover_foto:
            if perfil.foto:
                perfil.foto.delete(save=False)
                perfil.foto = None

        elif foto:
            perfil.foto = foto
            perfil.save()

            # Crop para centralizar e deixar quadrado
            if perfil.foto:
                img = Image.open(perfil.foto.path)
                width, height = img.size
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2

                img = img.crop((left, top, right, bottom))
                img = img.resize((300, 300))
                img.save(perfil.foto.path)

            return redirect('perfil_usuario', username=request.user.username)

        else:
            perfil.save()
            return redirect('perfil_usuario', username=request.user.username)

    return render(request, 'blog/editar_perfil.html', {'perfil': perfil})


@login_required
def notificacoes(request):
    # Lista notificações do usuário e marca como lidas
    notificacoes = request.user.notificacoes.order_by('-criada_em')
    notificacoes.update(lida=True)
    return render(request, 'blog/notificacoes.html', {'notificacoes': notificacoes})


@login_required
def deletar_notificacao(request, notificacao_id):
    # Permite deletar uma notificação
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.delete()
    return redirect('notificacoes')


@login_required
def estatisticas_usuario(request):
    # Mostra estatísticas do usuário
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


class UsernamePasswordResetView(PasswordResetView):
    # Redefinição de senha via username
    template_name = 'registration/password_reset_username_form.html'
    email_template_name = 'registration/password_reset_emaile.html'
    subject_template_name = 'registration/password_reset_subjecte.txt'
    success_url = reverse_lazy('password_reset_done')

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
                    html_email_template_name=self.email_template_name,
                    subject_template_name=self.subject_template_name,
                )
                messages.success(request, 'Um e-mail de redefinição foi enviado.')
                return redirect(self.success_url)
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

        return render(request, self.template_name)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_donee.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirme.html'
    success_url = reverse_lazy('password_reset_completee')

