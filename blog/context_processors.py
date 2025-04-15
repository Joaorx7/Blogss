from .models import Categoria, Notificacao
from .models import Perfil, Categoria
from django.contrib.auth.models import User
from django.conf import settings

def categorias_disponiveis(request):
    return {
        'categorias': Categoria.objects.all()
    }
def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        qtd = Notificacao.objects.filter(usuario=request.user, lida=False).count()
    else:
        qtd = 0
    return {'notificacoes_nao_lidas': qtd}

def extras_para_todas_as_paginas(request):
    categorias_populares = Categoria.objects.all().order_by('-post__id')[:5]  # Exemplo de populares
    total_usuarios = User.objects.count()

    perfis_recomendados = []
    if request.user.is_authenticated:
        seguindo_ids = request.user.perfil.seguindo.values_list('id', flat=True)
        perfis_recomendados = Perfil.objects.exclude(user__id__in=seguindo_ids).exclude(user=request.user)[:5]

    return {
        'categorias_populares': categorias_populares,
        'total_usuarios': total_usuarios,
        'perfis_recomendados': perfis_recomendados
    }

def media_url(request):
    return {'MEDIA_URL': settings.MEDIA_URL}