from django_filters import FilterSet, ModelMultipleChoiceFilter, CharFilter, BooleanFilter
from .models import Tag, Recipe


class CustomRecipeFilterSet(FilterSet):
    """Кастомные фильтры."""
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )
    author = CharFilter(lookup_expr='username')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

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
