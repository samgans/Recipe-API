from django.urls import path

from .views import UserCreationView, UserCreateTokenView, UserInformationView

app_name = 'user'

urlpatterns = [
    path('create/', UserCreationView.as_view(), name='create_user'),
    path('token/', UserCreateTokenView.as_view(), name='get_token'),
    path('profile/', UserInformationView.as_view(), name='view_user')
]
