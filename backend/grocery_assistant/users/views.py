from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .pagination import UserPagination
from .serializers import (NewUserSerializer, SetPasswordSerializer,
                          SubscriptionsSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    '''Вьюсет для работы с приложением users.'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        '''Ветвление пермишенов.'''
        # Если GET-list или POST запрос
        if self.action == 'list' or self.action == 'create':
            # Можно все
            return (permissions.AllowAny(),)
        # Для остальных ситуаций оставим текущий
        # перечень пермишенов без изменений
        return super().get_permissions()

    def get_serializer_class(self):
        '''Ветвление сериалайзеров.'''
        # При создании нового пользователя, выбираем другой сериализатор
        if self.action == 'create':
            return NewUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        '''Метод обрабатывающий эндпоинт me.'''
        user = get_object_or_404(User, email=request.user.email)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        '''Метод обрабатывающий эндпоинт set_password.'''
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
                return Response(
                    {'current_password': 'Вы ввели неверный пароль'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        '''
        Метод обрабатывающий эндпоинт subscriptions.
        Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        '''
        # авторизованный юзер
        user = request.user
        # объекты пользователей на которых подписан пользователь токена,
        # в связующей таблице Follow,
        # где выбраны все поля following(на кого подписан)
        queryset = User.objects.filter(following__user=user)
        # Передаем методу queryset, и возвращаем итерируемый объект,
        # содержащий только данные запрошенной страницы.
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            data=pages,
            many=True,
            context={
                'request': request
            },
        )
        serializer.is_valid()
        # передаем сериализованные данные страницы,
        # и возвращаем экземпляр Response
        return self.get_paginated_response(data=serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        '''Метод обрабатывающий эндпоинт subscribe.'''
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
            elif Follow.objects.filter(
                    following=interes_user,
                    user=request.user).exists():
                return Response(
                    {'errors': (
                        'Вы уже подписаны на пользователя '
                        + f'{interes_user.username}.'
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # подписываем пользователя
            Follow.objects.create(following=interes_user, user=request.user)
            # выводим информацию о новой подписке
            serializer = SubscriptionsSerializer(
                interes_user,
                context={
                    'request': request
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # если метод delete
        # проверяем существует ли уже такая подписка
        subscribe = Follow.objects.filter(
            following=interes_user,
            user=request.user
        )
        if subscribe:
            subscribe.delete()
            # удаляем подписку из связующей таблицы, если она там
            return Response(status=status.HTTP_204_NO_CONTENT)
        # иначе говорим что подписки не было
        return Response(
            {'errors': (
                'Вы не были подписаны на пользователя '
                + f'{interes_user.username}.'
            )},
            status=status.HTTP_400_BAD_REQUEST
        )
