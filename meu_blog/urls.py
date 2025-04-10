from django.contrib import admin
from django.urls import path
from blog import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseForbidden
from blog.views import termos_uso

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
    path('buscar-usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('deixar_de_seguir/<str:username>/', views.deixar_de_seguir_usuario, name='deixar_de_seguir_usuario'),
    path('seguir/<str:username>/', views.seguir_usuario, name='seguir_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'),
    path('feed/', views.feed_personalizado, name='feed'),
    path('termos-de-uso/', termos_uso, name='termos_uso'),
    # Redefinição de senha com link exibido na tela
    path('senha-reset/', views.PasswordResetViewDev.as_view(), name='password_reset'),
    path('senha-reset-enviado/', views.mostrar_link_reset, name='mostrar_link_reset'),
    path('senha-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('senha-reset-completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('mensagens/', views.caixa_de_entrada, name='caixa_de_entrada'),
    path('mensagem/<str:username>/', views.enviar_mensagem, name='enviar_mensagem'),
    path('comentario/editar/<int:comentario_id>/', views.editar_comentario, name='editar_comentario'),
    path('notificacao/deletar/<int:notificacao_id>/', views.deletar_notificacao, name='deletar_notificacao'),
    path('comentario/deletar/<int:comentario_id>/', views.deletar_comentario, name='deletar_comentario'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('estatisticas/', views.estatisticas_usuario, name='estatisticas'),
    path('erro403/', lambda request: HttpResponseForbidden("Acesso negado")),
]

# Arquivos de mídia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
