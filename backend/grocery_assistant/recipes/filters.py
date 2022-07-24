from django_filters import FilterSet, ModelMultipleChoiceFilter, CharFilter
from .models import Tag, Ingredient, Recipe


class CustomRecipeFilterSet(FilterSet):
    """Кастомные фильтры."""
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        label='tags',
        queryset=Tag.objects.all()
    )
    author = CharFilter(lookup_expr='username')



    '''is_favorited = CharFilter(method='filter_is_favorited')

    def filter_is_favorited(self, queryset, name, value):
        # construct the full lookup expression.
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: False})
        FavoritesRecipesUserList.objects.filter(user=user ,favorit_recipe=obj.pk).exists())'''



    class Meta:
        model = Recipe
        fields = ['tags', 'author',]# 'is_favorited',]

#"is_in_shopping_cart"