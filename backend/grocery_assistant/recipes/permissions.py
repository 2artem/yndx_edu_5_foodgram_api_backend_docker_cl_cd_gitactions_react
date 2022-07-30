from rest_framework import permissions
from django.urls import reverse


class AdminAllOnlyAuthorPermission(permissions.BasePermission):
    """
    Кастомный пермишн для работы администратора и
    автора объекта c небезопасными методами.
    """
    # права на уровне запроса и пользователя
    def has_permission(self, request, view):
        return True
        #return (
        #        request.method in permissions.SAFE_METHODS
        #        or request.user.is_authenticated
        #    )


        #return bool(request.user.is_superuser or request.user.is_admin)

        #if request.path == reverse('user-detail', kwargs={'username': 'me'}):
        #    # Если страница me, даем доступ
        #    return True
        # Если соответствующие эндпоинты users
        #return bool(request.user.is_superuser or request.user.is_admin)

    # права на уровне объекта
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_superuser
            or obj.author == request.user
            or request.user.groups.filter(name='recipes_admins').exists()
        )
