from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.urls import path
from core.consumers import EventConsumer
from django.core.asgi import get_asgi_application #Change No.1

application = ProtocolTypeRouter({
        'http': get_asgi_application(),
        'websocket':AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
            path('ws/',EventConsumer.as_asgi())
            ])
        )
    )
})