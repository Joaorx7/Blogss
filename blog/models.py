from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json

# ============================
# PERFIL DO USUÁRIO
# ============================

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    bio = models.TextField(blank=True)
    seguidores = models.ManyToManyField(User, related_name='seguindo', blank=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

# ============================
# CATEGORIA E TAG
# ============================

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

# ============================
# POSTAGEM
# ============================

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    curtidas = models.ManyToManyField(User, related_name='posts_curtidos', blank=True)
    imagem = models.ImageField(upload_to='imagens_posts/', blank=True, null=True)

    def __str__(self):
        return self.titulo

# ============================
# COMENTÁRIOS
# ============================

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    resposta_a = models.ForeignKey('self', null=True, blank=True, related_name='respostas', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comentário de {self.autor.username}'

# ============================
# MENSAGENS PRIVADAS
# ============================

class Mensagem(models.Model):
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    conteudo = models.TextField()
    enviada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    resposta_a = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='respostas')

    def __str__(self):
        return f'Mensagem de {self.remetente.username} para {self.destinatario.username}'

# ============================
# NOTIFICAÇÕES
# ============================

class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    texto = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.texto}"

@login_required
def chat(request, username):
    outro_usuario = get_object_or_404(User, username=username)
    mensagens = Mensagem.objects.filter(
        Q(remetente=request.user, destinatario=outro_usuario) |
        Q(remetente=outro_usuario, destinatario=request.user)
    ).order_by('enviada_em')

    return render(request, 'blog/chat.html', {
        'mensagens': mensagens,
        'outro_usuario': outro_usuario
    })

@login_required
def enviar_mensagem(request, username):
    if request.method == 'POST':
        data = json.loads(request.body)
        conteudo = data.get('mensagem')
        destinatario = get_object_or_404(User, username=username)

        mensagem = Mensagem.objects.create(
            remetente=request.user,
            destinatario=destinatario,
            conteudo=conteudo
        )

        return JsonResponse({'status': 'ok'})