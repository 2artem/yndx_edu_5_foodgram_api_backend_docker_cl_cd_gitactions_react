from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CustomRecipeFilterSet, IngredientSearchFilter
from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     ShoppingUserList, Tag)
from .pagination import RecipePagination
from .permissions import AdminAllOnlyAuthorPermission
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer)


class ListRetrieveModelViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    '''
    Кастомный базовый вьюсет:
    Вернуть список объектов (GET);
    Вернуть объект (GET);
    '''
    pass


def post_delete_relationship_user_with_object(
        request,
        pk,
        model,
        message):
    '''Добавление и удаление рецепта в связующей таблице для пользователя.'''
    # получаем рецепт по первичному ключу id
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        # проверяем что это будет не повторное добавление рецепта
        # в связующую таблицу
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
        # возвращаем ответ
        text = {
            'id': recipe.id,
            'name': recipe.name,
            'image': str(recipe.image),
            'cooking_time': recipe.cooking_time
        }
        return Response(text, status=status.HTTP_201_CREATED)
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
    '''Вьюсет для рецептов.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilterSet
    permission_classes = (
        permissions.IsAuthenticated,
        AdminAllOnlyAuthorPermission,
    )

    def get_permissions(self):
        '''Ветвление пермишенов.'''
        # Если GET-list или Get-detail запрос
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        # Для остальных ситуаций оставим текущий перечень
        # пермишенов без изменений
        return super().get_permissions()

    def get_serializer_class(self):
        '''При создании или обновлении рецепта, выбираем другой сериализатор'''
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        '''Ендпоинт для избранных рецептов.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=FavoritesRecipesUserList,
            message='избранном'
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        '''Ендпоинт для списка покупок.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=ShoppingUserList,
            message='списке покупок'
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        '''Ендпоинт для загрузки списка покупок.'''
        # Выбираем объекты СВЯЗЕЙ пользователя и рецептов из Списка покупок
        # из вспомогательной таблицы
        recipes_user_in_shoplist = ShoppingUserList.objects.filter(
            user=request.user
        )
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
        # добавляя аннотацию для каждого объекта
        # сумму количества ингредиентов
        queryset_ingredients = ingredients.annotate(
            sum_amount_ingredients=(Sum('ingredient_in_recipe__amount'))
        )
        # генерация файла со списком ингридиентов
        # для изготовления всех рецептов из списка покупок
        content = (
            'Ваш сервис, Продуктовый помощник, подготовил \nсписок '
            + 'покупок по выбранным рецептам:\n'
            + 50 * '_'
            + '\n\n'
        )
        if not queryset_ingredients:
            content += (
                'К сожалению, в списке ваших покупок пусто - '
                + 'поскольку Вы не добавили в него ни одного рецепта.'
            )
        else:
            for ingr in queryset_ingredients:
                content += (
                    f'\t•\t{ingr.name} ({ingr.measurement_unit}) — '
                    + f'{ingr.sum_amount_ingredients}\n\n'
                )
        # Вывод файла
        filename = 'my_shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename
        )
        return response


class TagViewSet(ListRetrieveModelViewSet):
    '''Вьюсет для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveModelViewSet):
    '''Вьюсет для ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
