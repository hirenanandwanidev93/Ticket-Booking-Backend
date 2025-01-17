from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include(("api.routers", "api"), namespace="api")),
    path("ws", include(("api.routers-ws", "api"), namespace="api_ws")),
]
