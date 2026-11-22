from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from user import models, serializers


class RegisterUserView(CreateAPIView):
    serializer_class = serializers.RegisterUserSerializer


class LoginUserView(APIView):
    def post(self, request: Request):
        serializer = serializers.LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({'token': token.key})


class LogoutUserView(APIView):
    """Delete the token, so it can't be used again."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request):
        request.auth.delete()
        return Response(status=204)


class MeView(RetrieveAPIView):
    """The profile of the user the token belongs to."""

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user


class EditorSettingView(APIView):
    """The default description that opens in the editor for a new event."""

    permission_classes = (IsAuthenticated,)

    def get_object(self, user) -> models.EditorSetting:
        setting, _ = models.EditorSetting.objects.get_or_create(user=user)
        return setting

    def get(self, request: Request):
        return Response(self.get_object(request.user).value)

    def post(self, request: Request):
        serializer = serializers.EditorSettingSerializer(instance=self.get_object(request.user), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
