from rest_framework import permissions


class AdminAllOnlyAuthorPermission(permissions.BasePermission):
    '''
    Кастомный пермишн для работы администратора и
    автора объекта c небезопасными методами.
    '''
    def has_object_permission(self, request, view, obj):
        '''Определяем права на уровне объекта.'''
        return bool(
            request.user.is_superuser
            or obj.author == request.user
            or request.user.groups.filter(name='recipes_admins').exists()
        )
