from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil

@receiver(pre_delete, sender=User)
def limpar_seguidores_antes_deletar_user(sender, instance, **kwargs):
    # Remove o usuário das listas de seguidores de outros perfis
    for perfil in Perfil.objects.all():
        perfil.seguidores.remove(instance)