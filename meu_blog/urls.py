from django.contrib import admin
from django.urls import path
from blog import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseForbidden
from blog.views import (
    CustomPasswordResetDoneView,
    UsernamePasswordResetView,
)
from blog.views import home, cadastro

urlpatterns = [
    path('admin/', admin.site.urls),

    # Páginas principais
    path('', views.home, name='home'),
    path('sobre/', views.sobre, name='sobre'),

    # Postagens
    path('post/<int:post_id>/', views.detalhes_post, name='detalhes_post'),
    path('novo/', views.novo_post, name='novo_post'),
    path('editar/<int:post_id>/', views.editar_post, name='editar_post'),
    path('deletar/<int:post_id>/', views.deletar_post, name='deletar_post'),
    path('curtir/<int:post_id>/', views.curtir_post, name='curtir_post'),
    path('categoria/<int:categoria_id>/', views.posts_por_categoria, name='posts_por_categoria'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', views.sair, name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),

    # Perfil e redes sociais
    path('buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),
    path('deixar-de-seguir/<str:username>/', views.deixar_de_seguir, name='deixar_de_seguir'),
    path('seguir_ou_nao/<str:username>/', views.seguir_ou_nao, name='seguir_ou_nao'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
    path('feed/', views.feed_personalizado, name='feed'),

    # Comentários e notificações
    path('comentario/editar/<int:comentario_id>/', views.editar_comentario, name='editar_comentario'),
    path('comentario/deletar/<int:comentario_id>/', views.deletar_comentario, name='deletar_comentario'),
    path('notificacao/deletar/<int:notificacao_id>/', views.deletar_notificacao, name='deletar_notificacao'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),

    # Estatísticas e termos
    path('estatisticas/', views.estatisticas_usuario, name='estatisticas'),

    # Página de erro 403
    path('erro403/', lambda request: HttpResponseForbidden("Acesso negado")),

    # Fluxo de redefinição de senha por NOME DE USUÁRIO
    path('redefinir/', UsernamePasswordResetView.as_view(), name='password_reset'),
    path('redefinir/enviado/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('redefinir/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/redefinir/completo/'
    ), name='password_reset_confirm'),
    path('redefinir/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

]

# Arquivos de mídia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
