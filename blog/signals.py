from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil

#Define sinais que são executados automaticamente após certas ações (ex: criar perfil quando um usuário for criado).


# Sinal executado antes da exclusão de um usuário
@receiver(pre_delete, sender=User)
def limpar_seguidores_antes_deletar_user(sender, instance, **kwargs):
    # Remove o usuário que será deletado da lista de seguidores de todos os perfis
    for perfil in Perfil.objects.all():
        perfil.seguidores.remove(instance)