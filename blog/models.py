from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    bio = models.TextField(blank=True)
    seguidores = models.ManyToManyField(User, related_name='seguindo', blank=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def seguindo(self):
        return Perfil.objects.filter(seguidores=self.user)


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)


class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    curtidas = models.ManyToManyField(User, related_name='posts_curtidos', blank=True)
    imagem = models.ImageField(upload_to='imagens_posts/', blank=True, null=True)

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    resposta_a = models.ForeignKey('self', null=True, blank=True, related_name='respostas', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comentário de {self.autor.username}'


class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    texto = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.texto}"
