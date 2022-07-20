from django.urls import path
from django.urls import include
from .views import signup_to_api
from .views import issue_a_token
from rest_framework.routers import SimpleRouter
from .views import UserViewSet
#from .views import SubscribeViewSet


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
    # http://localhost/api/auth/token/login/

    #path('users/signup/', signup_to_api),
    #path('auth/token/login/', issue_a_token),
    # Удаляет токен текущего пользователя
    # http://localhost/api/auth/token/logout/
]
