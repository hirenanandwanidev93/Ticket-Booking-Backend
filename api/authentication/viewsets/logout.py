from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.authentication.models import ActiveSession


class LogoutViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        print("inside LogoutViewSet")
        print(request)
        user = request.user

        sessions = ActiveSession.objects.filter(user=user)
        for session in sessions:
            session.delete()

        return Response(
            {"success": True, "msg": "Token revoked"}, status=status.HTTP_200_OK
        )
