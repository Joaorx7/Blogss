from .models import Categoria, Notificacao
from .models import Perfil, Categoria
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Count

#Define funções que injetam dados automaticamente em todos os templates renderizados, como categorias, perfis recomendados, notificações, etc.

# Retorna todas as categorias para uso em contextos globais
def categorias_disponiveis(request):
    return {
        'categorias': Categoria.objects.all()
    }

# Retorna a quantidade de notificações não lidas do usuário autenticado
def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        qtd = Notificacao.objects.filter(usuario=request.user, lida=False).count()
    else:
        qtd = 0
    return {'notificacoes_nao_lidas': qtd}

# Retorna dados extras para todas as páginas do site: categorias populares, total de usuários e perfis recomendados
def extras_para_todas_as_paginas(request):
    categorias_populares = Categoria.objects.all().order_by('-post__id')[:5]  # Ordena pelas categorias com posts mais recentes
    total_usuarios = User.objects.count()  # Conta o total de usuários registrados

    perfis_recomendados = []
    if request.user.is_authenticated:
        # Obtém os perfis que o usuário atual não segue ainda
        seguindo_ids = request.user.perfil.seguindo.values_list('id', flat=True)
        perfis_recomendados = Perfil.objects.exclude(user__id__in=seguindo_ids).exclude(user=request.user)[:5]

    return {
        'categorias_populares': categorias_populares,
        'total_usuarios': total_usuarios,
        'perfis_recomendados': perfis_recomendados
    }

# Adiciona a URL base de arquivos de mídia no contexto
def media_url(request):
    return {'MEDIA_URL': settings.MEDIA_URL}

# Retorna as 10 categorias com mais posts (categorias principais)
def categorias_principais(request):
    return {
        'categorias_principais': Categoria.objects.annotate(num_posts=Count('post')).order_by('-num_posts')[:10]
    }
