from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework.pagination import BasePagination, PageNumberPagination
from rest_framework import status
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .pagination import UserPagination
from .serializers import UserSerializer, SetPasswordSerializer, SubscriptionsSerializer
from .permissions import UnAuthUsersViewUsersListAndMaySignToAPI
from rest_framework.decorators import api_view
from .serializers import FollowSerializer
from .serializers import NewUserSerializer
from .models import Follow
from rest_framework import mixins
#from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с приложением users."""
    #lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('^username',)
    permission_classes = (
        #UnAuthUsersViewUsersListAndMaySignToAPI,
        permissions.IsAuthenticated,
    #    AdminAllPermissionOrMeURLGetUPDMyself,
    )

    
    def get_serializer_class(self):
        # При создании нового пользователя, выбираем другой сериализатор
        if self.action == 'create':
            return NewUserSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            return (UnAuthUsersViewUsersListAndMaySignToAPI(),)
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Метод обрабатывающий эндпоинт 'me'."""
        user = get_object_or_404(User, email=request.user.email)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Метод обрабатывающий эндпоинт 'set_password'."""
        user = get_object_or_404(User, email=request.user.email)
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            if check_password(request.data['current_password'], user.password):
                # хешируем новый пароль
                new_password = make_password(request.data['new_password'])
                user.password = new_password
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'current_password': 'Вы ввели неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







####@action(detail=False, permission_classes=[permissions.IsAuthenticated])
    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        '''
        #Метод обрабатывающий эндпоинт 'subscriptions'.
        #Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты.
        '''


        # авторизованный юзер
        user = request.user
        # объекты пользователей в связующей таблице Follow, где
        # все поля following(на кого подписан) связаны с пользователем из токена
        queryset = User.objects.filter(following__user=user)
 


        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            data=pages, many=True, context={"request": request}
        )
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)






    @action(detail=True, methods=['post', 'delete']) #perm IsAut
    def subscribe(self, request, pk=None):
        '''.'''
        # получаем интересующего пользователя из url
        interes_user = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            # проверяем что подписка происходит не на самого себя
            if request.user == interes_user:
                return Response(
                    {'errors': 'Невозможно подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # проверяем что это будет не повторная подписка на пользователя
            elif Follow.objects.filter(following=interes_user, user=request.user).exists():
                return Response(
                    {'errors': f'Вы уже подписаны на пользователя {interes_user.username}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # подписываем пользователя
            Follow.objects.create(following=interes_user, user=request.user)
            # выводим информацию о новой подписке
            serializer = SubscriptionsSerializer(
                interes_user,
                context={
                    'request': request,
                    'interes_user': interes_user
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # если метод delete
        # проверяем существует ли уже такая подписка
        subscribe = Follow.objects.filter(following=interes_user, user=request.user)
        if subscribe:
            subscribe.delete()
            # удаляем подписку из связующей таблицы, если она там
            return Response(status=status.HTTP_204_NO_CONTENT)
        # иначе говорим что подписки не было
        return Response(
            {'errors': f'Вы не были подписаны на пользователя {interes_user.username}.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CreateListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Кастомный базовый вьюсет:
    Создает объект (для обработки запросов POST) и
    возвращает список объектов (для обработки запросов GET).
    """
    pass

class FollowViewSet(CreateListViewSet):
    """Предустановленный класс для работы с моделью Follow."""
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^following__username',)

    def get_queryset(self):
        """Изменяем базовый QuerySet, переопределив метод get_queryset."""
        new_qweryset = Follow.objects.filter(user=self.request.user)
        return new_qweryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
