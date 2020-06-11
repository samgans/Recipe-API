from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, UserTokenSerializer


class UserCreationView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserCreateTokenView(ObtainAuthToken):
    serializer_class = UserTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserInformationView(generics.RetrieveUpdateAPIView):
    '''View of user profile, patching profile'''

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        '''Retrieve authenticated user'''
        return self.request.user
