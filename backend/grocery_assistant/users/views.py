from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .pagination import UserPagination
from .serializers import UserSerializer, SetPasswordSerializer
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
    pagination_class = UserPagination # LimitOffsetPagination
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

# 

        '''# Если username и email не переданы
        request.POST._mutable = True
        request.data['email'] = request.user.email
        request.data['username'] = request.user.username
        request.POST._mutable = False
        # Сериализуем данные
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            # Проверка что роль может изменить только admin или superuser
            if 'role' in request.data:
                if user.is_superuser or user.is_admin:
                    serializer.save()
                    return Response(
                        serializer.data,
                        status=status.HTTP_200_OK
                    )
                return Response(
                    {'role': 'user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Метод обрабатывающий эндпоинт 'subscriptions'."""
        return Response(
                    {'role2': 'use2r'},
                    status=status.HTTP_400_BAD_REQUEST
                )

'''class SubscribeViewSet(viewsets.ModelViewSet):
    """Вьюсет для Review."""
    serializer_class = ReviewSerializer
    #permission_classes = (
    #    IsAuthenticatedOrReadOnly,
    #    AdminAllOnlyAuthorPermission,
    #)
    #filter_backends = (filters.SearchFilter,)
    #pagination_class = ReviewPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_qweryset = Review.objects.filter(title=title)
        return new_qweryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)'''

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

