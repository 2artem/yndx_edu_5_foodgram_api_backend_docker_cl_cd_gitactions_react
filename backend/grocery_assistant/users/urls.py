from django.urls import path
from django.urls import include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet
from djoser.views import TokenCreateView, TokenDestroyView


router = SimpleRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    # Роутер для users/
    path('', include(router.urls)),
    # Используется для получения токена по емейлу и паролю
    path('auth/token/login/', TokenCreateView.as_view()),
    # Удаляет токен текущего пользователя
    path('auth/token/logout/', TokenDestroyView.as_view()),
]
