from api.ticketRelay.views import (
    WsViewSet
)
from rest_framework import routers
from api.user.viewsets import UserViewSet

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"", WsViewSet, basename="ws-connections")

urlpatterns = [
    *router.urls,
]
