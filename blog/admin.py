from django.contrib import admin
from .models import Post, Categoria, Comentario, Notificacao, Perfil, Tag  # adicione Tag

admin.site.register(Post)
admin.site.register(Categoria)
admin.site.register(Comentario)
admin.site.register(Notificacao)
admin.site.register(Perfil)
admin.site.register(Tag)  # aqui