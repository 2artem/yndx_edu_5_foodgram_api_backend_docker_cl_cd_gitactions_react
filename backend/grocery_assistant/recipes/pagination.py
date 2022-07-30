from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    '''Пагинация рецептов по параметрам limit и page.'''
    page_size_query_param = 'limit'
