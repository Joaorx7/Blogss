from .models import Categoria, Notificacao

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