from django.urls import path
from django.urls import include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet
#from .views import SubscribeViewSet
from djoser.views import TokenCreateView, TokenDestroyView


router = SimpleRouter()
router.register('users', UserViewSet, basename='users')

'''router.register(
    r'users/(?P<id>[\d]+)/subscribe',
    SubscribeViewSet,
    basename='review'
)'''


urlpatterns = [
    # Изменение пароля текущего пользователя
    # POST path('users/set_password/', signup_to_api),
    # Роутер для users/
    path('', include(router.urls)),
    # Получить токен авторизации

    # Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.
    path('auth/token/login/', TokenCreateView.as_view()),
    # Удаляет токен текущего пользователя
    
    path('auth/token/logout/', TokenDestroyView.as_view()),

    

]
