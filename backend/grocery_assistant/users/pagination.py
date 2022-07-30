from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict


class UserPagination(PageNumberPagination):
    '''Пагинация пользователей по параметрам limit и page.'''
    page_size_query_param = 'limit'
