"""
WSGI config for meu_blog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
#Interface padrão para servidores web como Gunicorn e uWSGI executarem o projeto Django em produção.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_blog.settings')

application = get_wsgi_application()
