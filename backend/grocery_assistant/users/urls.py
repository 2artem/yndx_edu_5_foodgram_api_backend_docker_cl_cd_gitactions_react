from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import SimpleRouter

from .views import UserViewSet

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
