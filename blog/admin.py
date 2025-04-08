from django.contrib import admin
from .models import Post, Comentario, Categoria  # certifique-se de importar Categoria

# Registra os modelos no admin
admin.site.register(Post)
admin.site.register(Comentario)
admin.site.register(Categoria)