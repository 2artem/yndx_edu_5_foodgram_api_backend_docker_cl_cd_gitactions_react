from django_filters import rest_framework
from .models import Title


class CustomFilter(rest_framework.FilterSet):
    """Кастомные фильтры."""
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = rest_framework.NumberFilter(field_name='year')
    genre = rest_framework.CharFilter(field_name='genre__slug')
    category = rest_framework.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', 'genre', 'category']
