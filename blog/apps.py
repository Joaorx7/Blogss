from django.apps import AppConfig

#Define a configuração do app, incluindo seu nome. É utilizado internamente pelo Django.
#como categorias, perfis recomendados, notificações, etc.

# Classe de configuração principal do app "blog"
class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Define o tipo de campo padrão para chaves primárias
    name = 'blog'  # Nome da aplicação, usado pelo Django para registro

# Segunda definição da classe BlogConfig com suporte a signals
class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Mesmo campo padrão definido anteriormente
    name = 'blog'  # Nome da aplicação

    def ready(self):
        import blog.signals  # Importa os signals quando a aplicação é carregada
