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


from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from selectors import SelectSelector
from rest_framework.decorators import action
from urllib3 import HTTPResponse
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer, RecipeCreateUpdateSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import Recipe, Tag, Ingredient, FavoritesRecipesUserList, ShoppingUserList, RecipeIngredientRelationship
from rest_framework import mixins
from .pagination import RecipePagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CustomRecipeFilterSet
from rest_framework import filters



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


def post_delete_relationship_user_with_object(
    request,
    pk,
    model,
    message):
    '''Добавление и удаление рецепта в связующей таблице для пользователя.'''
    # получаем рецепт по первичному ключу id
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        # проверяем что это будет не повторное добавление в рецепта в связующую таблицу
        if model.objects.filter(
            recipe=recipe,
            user=request.user).exists():
            return Response(
                {'errors': f'Рецепт с номером {pk} уже у Вас в {message}.'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(
            recipe=recipe,
            user=request.user
        )
        text = {
            'id': recipe.id,
            'name': recipe.name,
            'image': recipe.image,
            'cooking_time': recipe.cooking_time
        }
        return Response(text ,status=status.HTTP_201_CREATED)
    # если метод delete
    # проверяем есть ли рецепт в связующей таблице
    obj_recipe = model.objects.filter(
        recipe=recipe,
        user=request.user
    )
    if obj_recipe:
        obj_recipe.delete()
        # удаляем рецепт из связующей таблицы, если он там
        return Response(status=status.HTTP_204_NO_CONTENT)
    # иначе говорим что в не было
    return Response(
        {'errors': f'Рецепта с номером {pk} нет у Вас в {message}.'},
        status=status.HTTP_400_BAD_REQUEST
    )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для Category."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilterSet
    #permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,)

    def get_serializer_class(self):
        # При создании или обновлении рецепта, выбираем другой сериализатор
        # if self.request.method in ('POST', 'PATCH'):
        if self.action == 'create' or self.action == 'partial_update' or self.action == 'update':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer
    
    @action(detail=True, methods=['post', 'delete']) #perm IsAut
    def favorite(self, request, pk=None):
        '''.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=FavoritesRecipesUserList,
            message='избранном'
        )

    @action(detail=True, methods=['post', 'delete']) #perm IsAut
    def shopping_cart(self, request, pk=None):
        '''.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=ShoppingUserList,
            message='списке покупок'
        )

    @action(detail=False, methods=['get']) #perm IsAut
    def download_shopping_cart(self, request):
        '''.'''
        # Выбираем объекты СВЯЗЕЙ пользователя и рецептов из Списка покупок
        # из вспомогательной таблицы
        recipes_user_in_shoplist = ShoppingUserList.objects.filter(user=request.user)
        # Выбираем объекты РЕЦЕПТОВ пользователя из Списка покупок
        recipes = Recipe.objects.filter(
            recipe_in_shoplist__in=recipes_user_in_shoplist
        )
        # Выбираем объекты всех ИНГРИДИЕНТОВ 
        # у которых в связующей таблице, рецепты равны - рецептам из выборки
        ingredients = Ingredient.objects.filter(
            ingredient_in_recipe__recipe__in=recipes
        )
        # тематически объединяем одинаковые ИНГРИДИЕНТЫ,
        # добавляя аннотацию для каждого объекта - сумму количества ингредиентов
        queryset_ingredients = ingredients.annotate(
            sum_amount_ingredients=(Sum('ingredient_in_recipe__amount'))
        )
        # генерация файла со списком ингридиентов
        # для изготовления всех рецептов из списка покупок
        content = (
            'Ваш сервис, Продуктовый помощник, подготовил \nсписок '
            +'покупок по выбранным рецептам:\n'
            + 50*'_'
            +'\n\n'
        )
        if not queryset_ingredients:
            content += (
                'К сожалению, в списке ваших покупок пусто - '
                +'поскольку Вы не добавили в него ни одного рецепта.'
            )
        else:
            for ingr in queryset_ingredients:
                content += (
                    f'\t•\t{ingr.name} ({ingr.measurement_unit}) — '
                    +f'{ingr.sum_amount_ingredients}\n\n'
                )
        # Вывод файла
        filename = 'my_shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response


class TagViewSet(ListRetrieveModelViewSet):
    """Вьюсет для ."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    #permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,) ADMIN ili READONLY

class IngredientViewSet(ListRetrieveModelViewSet):
    """Вьюсет для ."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('^name',)
    #permission_classes = (IsAuthenticatedOrReadOnly, AdminAllPermission,) ADMIN ili READONLY
