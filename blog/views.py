from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PostForm
from django.shortcuts import render
from .models import Post, Categoria
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
from .models import Mensagem
from .forms import MensagemForm
import markdown

def buscar_usuarios(request):
    termo = request.GET.get('q', '')
    usuarios = User.objects.filter(username__icontains=termo)
    return render(request, 'blog/buscar_usuarios.html', {
        'usuarios': usuarios,
        'termo': termo
    })

def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    posts = Post.objects.filter(autor=usuario).order_by('-criado_em')
    return render(request, 'blog/perfil_usuario.html', {
        'usuario': usuario,
        'posts': posts
    })

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

def home(request):
    posts_lista = Post.objects.all().order_by('-criado_em')
    paginator = Paginator(posts_lista, 5)  # 5 posts por página
    pagina = request.GET.get('page')
    posts = paginator.get_page(pagina)
    categorias = Categoria.objects.all()

    return render(request, 'blog/home.html', {'posts': posts, 'categorias': categorias})

def detalhes_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comentarios = post.comentarios.all().order_by('-criado_em')
    categorias = Categoria.objects.all()

    # Converte o conteúdo do post em HTML usando markdown
    post_conteudo_html = markdown.markdown(post.conteudo)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ComentarioForm(request.POST)
            if form.is_valid():
                comentario = form.save(commit=False)
                comentario.post = post
                comentario.autor = request.user
                comentario.save()
                return redirect('detalhes_post', post_id=post.id)
        else:
            return redirect('login')
    else:
        form = ComentarioForm()

    return render(request, 'blog/detalhes_post.html', {
        'post': post,
        'post_conteudo_html': post_conteudo_html,
        'comentarios': comentarios,
        'form': form,
        'categorias': categorias
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

def curtir_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.curtidas.all():
        post.curtidas.remove(request.user)
        curtido = False
    else:
        post.curtidas.add(request.user)
        curtido = True

    return JsonResponse({'curtido': curtido, 'total': post.curtidas.count()})

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
    mensagens_recebidas = Mensagem.objects.filter(destinatario=request.user).order_by('-enviada_em')
    return render(request, 'blog/caixa_de_entrada.html', {
        'mensagens': mensagens_recebidas
    })