from django_filters import AllValuesMultipleFilter
from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class CustomRecipeFilterSet(filters.FilterSet):
    '''Кастомные фильтры.'''
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )
    author = AllValuesMultipleFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def _bool_filter(self, key, value, queryset, user):
        '''Фильтрация для логических ключей.'''
        map_dict = {f'{key}__user': user}
        if not user.is_anonymous:
            if value:
                # если ключ True
                return queryset.filter(**map_dict)
            elif value is False:
                # Если ключ False
                return queryset.exclude(**map_dict)
        # неавторизованый пользователь получит все записи
        # авторизованный получит все записи при нелогическом значении ключа
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        '''Показывать только рецепты, находящиеся в списке избранного.'''
        key = 'favorit_recipe'
        return self._bool_filter(key, value, queryset, user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        '''Показывать только рецепты, находящиеся в списке покупок.'''
        key = 'recipe_in_shoplist'
        return self._bool_filter(key, value, queryset, user=self.request.user)

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']


class IngredientSearchFilter(filters.FilterSet):
    '''Поиск по наименованию ингредиента.'''
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
