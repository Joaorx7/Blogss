from django.contrib import admin  # Importa o módulo de administração do Django
from .models import Post, Categoria, Comentario, Notificacao, Perfil, Tag  # Importa os modelos definidos na aplicação atual

# Registra cada modelo no painel administrativo do Django
# Isso permite que os dados desses modelos possam ser visualizados e manipulados pela interface administrativa

admin.site.register(Post)         # Registra o modelo Post
admin.site.register(Categoria)    # Registra o modelo Categoria
admin.site.register(Comentario)   # Registra o modelo Comentario
admin.site.register(Notificacao)  # Registra o modelo Notificacao
admin.site.register(Perfil)       # Registra o modelo Perfil
admin.site.register(Tag)          # Registra o modelo Tag