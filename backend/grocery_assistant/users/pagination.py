from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    '''Пагинация пользователей по параметрам limit и page.'''
    page_size_query_param = 'limit'


class SubscriptionsPagination(PageNumberPagination):
    '''.'''
    page_size_query_param = 'limit'
    """def paginate_queryset(self, queryset, request, view=None):
        '''
        The paginate_queryset method is passed to the initial queryset and
        should return an iterable object. That object contains only the data in the requested page.

        Метод paginate_queryset передается начальному набору запросов и должен возвращать
        итерируемый объект. Этот объект содержит только данные запрошенной страницы.

        paginate_queryset(self, queryset, request, view=None): в него передаётся исходный queryset,
        а возвращает он итерируемый объект, содержащий только данные запрашиваемой страницы;

        для объектов
        '''
        pass

        

    
    def get_paginated_response(self, data):
        '''
        The get_paginated_response method is passed to the
        serialized page data and should return a Response instance.

        Метод get_paginated_response передается сериализованным данным
        страницы и должен возвращать экземпляр Response.

        принимает сериализованные данные страницы, возвращает экземпляр Response.

        для выдачи результата сериализации

        '''
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))"""
