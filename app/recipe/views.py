from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe.serializers import TagSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    '''
    A viewset for tag creation and listing
    '''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        return (
            Tag.objects.all().filter(owner=self.request.user).order_by('-name')
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
