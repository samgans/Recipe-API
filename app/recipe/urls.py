from django.urls import include, path

from rest_framework.routers import DefaultRouter

from recipe.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'recipe'

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
