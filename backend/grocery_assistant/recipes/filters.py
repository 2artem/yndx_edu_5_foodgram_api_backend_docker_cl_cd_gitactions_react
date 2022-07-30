#from django_filters import FilterSet, ModelMultipleChoiceFilter, CharFilter, BooleanFilter
from django_filters import rest_framework as filters
from .models import Ingredient, Tag, Recipe


class CustomRecipeFilterSet(filters.FilterSet):
    """Кастомные фильтры."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )
    author = filters.CharFilter(lookup_expr='username')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        '''Показывать только рецепты, находящиеся в списке избранного.'''
        if not self.request.user.is_anonymous:
            if value:
                # если ключ True
                return queryset.filter(favorit_recipe__user=self.request.user)
            elif value == False:
                # Если ключ False
                return queryset.exclude(favorit_recipe__user=self.request.user)
            # если ключа нет
        # неавторизованый пользователь получит все записи
        # авторизованный получит все записи при нелогическом значении ключа
        return queryset


    def filter_is_in_shopping_cart(self, queryset, name, value):
        '''Показывать только рецепты, находящиеся в списке покупок.'''
        if not self.request.user.is_anonymous:
            if value:
                # если ключ True
                return queryset.filter(recipe_in_shoplist__user=self.request.user)
            elif value == False:
                # Если ключ False
                return queryset.exclude(recipe_in_shoplist__user=self.request.user)
        # неавторизованый пользователь получит все записи
        # авторизованный получит все записи при нелогическом значении ключа
        return queryset


    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
