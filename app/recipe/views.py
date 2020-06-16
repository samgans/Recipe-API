from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer, \
                               RecipeSerializer, RecipeDetailSerializer, \
                               RecipeImageSerializer


class RecipePartsBaseViewSet(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    '''Base viewset for both tags and ingredients'''
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(RecipePartsBaseViewSet):
    '''Retrieve, update or create new tag'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RecipePartsBaseViewSet):
    '''Retrieve, update or create new ingredient'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    '''Retrieve, update or create new recipe'''
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        return Recipe.objects.all().filter(
            owner=self.request.user
        ).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        else:
            return self.serializer_class

    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

