"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter,get_default_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

application=get_default_application()