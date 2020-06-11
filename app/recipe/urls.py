from django.urls import include, path

from rest_framework.routers import DefaultRouter

from recipe.views import TagViewSet

app_name = 'recipe'

router = DefaultRouter()
router.register(r'', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
