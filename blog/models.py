from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

#Define os modelos de dados do seu sistema (ex: Post, Comentario, Perfil, etc). Cada modelo representa uma tabela no banco de dados.

# Modelo que representa o perfil de um usuário, com foto, biografia e seguidores.
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')  # Um perfil para cada usuário
    bio = models.TextField(blank=True)  # Campo opcional para biografia
    seguidores = models.ManyToManyField(User, related_name='seguindo', blank=True)  # Relação de seguidores
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)  # Foto de perfil

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def seguindo(self):
        # Retorna os perfis que o usuário está seguindo
        return Perfil.objects.filter(seguidores=self.user)

# Cria automaticamente um perfil sempre que um novo usuário é registrado
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

# Modelo de categoria usada para classificar posts
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

# Modelo para tags associadas aos posts
class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome

# Modelo principal do blog, representando um post
class Post(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    curtidas = models.ManyToManyField(User, related_name='posts_curtidos', blank=True)
    imagem = models.ImageField(upload_to='imagens_posts/', blank=True, null=True)

    def __str__(self):
        return self.titulo

# Modelo para comentários feitos nos posts
class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    resposta_a = models.ForeignKey('self', null=True, blank=True, related_name='respostas', on_delete=models.CASCADE)  # Comentários encadeados (respostas)

    def __str__(self):
        return f'Comentário de {self.autor.username}'

# Modelo para armazenar notificações de ações no sistema
class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')  # Usuário que recebe a notificação
    texto = models.CharField(max_length=255)  # Texto da notificação
    lida = models.BooleanField(default=False)  # Se a notificação foi lida
    criada_em = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)  # Link para a ação referenciada

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.texto}"

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
