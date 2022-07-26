'''from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import AdminAllPermission
from .permissions import AdminAllOnlyAuthorPermission
from .models import Category
from .models import Genre
from .models import Title
from .models import Review
from .models import Comment
from .serializers import TitlesSerializerMethod
from .serializers import TitlesSerializer
from .serializers import CategorySerializer
from .serializers import GenreSerializer
from .serializers import ReviewSerializer
from .serializers import CommentSerializer
from .pagination import CategoryPagination
from .pagination import GenrePagination
from .pagination import TitlesPagination
from .pagination import ReviewPagination
from .pagination import CommentPagination
from .filters import CustomFilter'''

from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer, RecipeCreateUpdateSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import Recipe, Tag, Ingredient
from rest_framework import mixins
from .pagination import RecipePagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomRecipeFilterSet



class ListCreateDestroyModelViewSet(mixins.CreateModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    '''
    Кастомный базовый вьюсет:
    Вернуть список объектов (для обработки запросов GET);
    Создать объект (для обработки запросов POST);
    Удалить объект (для обработки запросов DELETE).
    '''
    pass


class ListRetrieveModelViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    '''
    Кастомный базовый вьюсет:
    Вернуть список объектов (GET);
    Вернуть объект (GET);
    '''
    pass


'''class GenreViewSet(ListCreateDestroyModelViewSet):
    """Вьюсет для Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,)
    pagination_class = GenrePagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class CategoryViewSet(ListCreateDestroyModelViewSet):
    """Вьюсет для Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,)
    pagination_class = CategoryPagination
    search_fields = ('^name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет для Title."""
    queryset = (Title.objects.annotate(
        rating=Avg('review__score')).order_by('year'))
    permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,)
    pagination_class = TitlesPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesSerializer
        return TitlesSerializerMethod


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для Review."""
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminAllOnlyAuthorPermission,
    )
    filter_backends = (filters.SearchFilter,)
    pagination_class = ReviewPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_qweryset = Review.objects.filter(title=title)
        return new_qweryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для Comment."""
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminAllOnlyAuthorPermission,
    )
    pagination_class = CommentPagination

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_qweryset = Comment.objects.filter(review=review)
        return new_qweryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(
            author=self.request.user,
            review=review
        )
        '''


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для Category."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend,)
    # Фильтровать будем по пол tags модели Recipe
    #filterset_fields = ('tags',)
    filterset_class = CustomRecipeFilterSet

    #filterset_fields = ('is_favorited',)
    '''
    permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,)
    search_fields = ('^name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)'''
    def get_serializer_class(self):
        # При создании или обновлении рецепта, выбираем другой сериализатор
        if self.action == 'create' or self.action == 'partial_update' or self.action == 'update':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer



class TagViewSet(ListRetrieveModelViewSet):
    """Вьюсет для ."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(ListRetrieveModelViewSet):
    """Вьюсет для ."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    
    #Поиск по ингредиентам

#Ищите ингредиенты по полю name регистронезависимо, по вхождению в начало названия.

#В качестве усложнения можно сделать двойную фильтрацию:
###	по вхождению в начало названия;
### по вхождению в произвольном месте.

#Сортировка в таком случае должна быть от первых ко вторым.


