"""
URL configuration for meu_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseForbidden

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),
    path('post/<int:post_id>/', views.detalhes_post, name='detalhes_post'),
    path('novo/', views.novo_post, name='novo_post'),
    path('editar/<int:post_id>/', views.editar_post, name='editar_post'),
    path('deletar/<int:post_id>/', views.deletar_post, name='deletar_post'),
    path('curtir/<int:post_id>/', views.curtir_post, name='curtir_post'),
    path('categoria/<int:categoria_id>/', views.posts_por_categoria, name='posts_por_categoria'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', views.sair, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
    path('buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),
    path('deixar-de-seguir/<str:username>/', views.deixar_de_seguir_usuario, name='deixar_de_seguir_usuario'),
    path('feed/', views.feed_personalizado, name='feed'),
    path('mensagens/', views.caixa_de_entrada, name='caixa_de_entrada'),
    path('mensagem/<str:username>/', views.enviar_mensagem, name='enviar_mensagem'),
    path('erro403/', lambda request: HttpResponseForbidden("Acesso negado")),
]

# Arquivos de mídia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
