from django import template

register = template.Library()

@register.filter
def segue_usuario(usuario, autor):
    if usuario.is_authenticated:
        return autor in usuario.perfil.seguindo.all()
    return False