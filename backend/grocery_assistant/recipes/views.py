'''from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import AdminAllPermission
from .permissions import AdminAllOnlyAuthorPermission
from .filters import CustomFilter'''

from rest_framework import permissions
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
from .filters import CustomRecipeFilterSet, IngredientSearchFilter
from rest_framework import filters
from .permissions import AdminAllOnlyAuthorPermission


class ListRetrieveModelViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    '''
    Кастомный базовый вьюсет:
    Вернуть список объектов (GET);
    Вернуть объект (GET);
    '''
    pass


'''
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
    permission_classes = (AdminAllOnlyAuthorPermission,)

    def get_permissions(self):
        # Если GET-list или Get-detail запрос
        if self.action == 'list' or self.action == 'retrieve':
            return (permissions.AllowAny(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions() 


    def get_serializer_class(self):
        # При создании или обновлении рецепта, выбираем другой сериализатор
        
        if self.action == 'create' or self.action == 'partial_update' or self.action == 'update':
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    #def perform_create(self, serialaizer):
    #    serialaizer.save(author=self.request.user)
    
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


class IngredientViewSet(ListRetrieveModelViewSet):
    """Вьюсет для ."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


'''class FollowViewSet(CreateListViewSet):
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
        serializer.save(user=self.request.user)'''
