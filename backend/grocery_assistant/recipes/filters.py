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
        '''.'''
        if not self.request.user.is_anonymous:
            if value:
                return queryset.filter(favorit_recipe__user=self.request.user)
            return queryset.exclude(favorit_recipe__user=self.request.user)
        return queryset


    def filter_is_in_shopping_cart(self, queryset, name, value):
        '''.'''
        if not self.request.user.is_anonymous:
            if value:
                return queryset.filter(recipe_in_shoplist__user=self.request.user)
            return queryset.exclude(recipe_in_shoplist__user=self.request.user)
        return queryset


    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
