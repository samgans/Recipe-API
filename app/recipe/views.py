from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer, \
                               RecipeSerializer, RecipeDetailSerializer


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
        else:
            return self.serializer_class
