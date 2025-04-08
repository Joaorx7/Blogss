from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PostForm
from django.shortcuts import render
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ComentarioForm
from django.contrib.auth import logout
from django.core.paginator import Paginator
from .models import Categoria

@login_required
def novo_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PostForm()

    return render(request, 'blog/novo_post.html', {'form': form})

from django.core.paginator import Paginator

def home(request):
    posts_lista = Post.objects.all().order_by('-criado_em')
    paginator = Paginator(posts_lista, 5)  # 5 posts por página

    pagina = request.GET.get('page')
    posts = paginator.get_page(pagina)

    return render(request, 'blog/home.html', {'posts': posts})

def detalhes_post(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/detalhes_post.html', {'post': post})

def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'blog/cadastro.html', {'form': form})

@login_required
def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.autor != request.user:
        messages.error(request, 'Você não tem permissão para editar este post.')
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detalhes_post', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/editar_post.html', {'form': form})

@login_required
def deletar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.autor != request.user:
        messages.error(request, 'Você não tem permissão para excluir este post.')
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'blog/deletar_post.html', {'post': post})

def detalhes_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comentarios = post.comentarios.all().order_by('-criado_em')

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
        'comentarios': comentarios,
        'form': form
    })

@login_required
def sair(request):
    logout(request)
    return redirect('home')

def posts_por_categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    posts = Post.objects.filter(categoria=categoria).order_by('-criado_em')
    return render(request, 'blog/posts_por_categoria.html', {'categoria': categoria, 'posts': posts})