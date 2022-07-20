from rest_framework import permissions
from django.urls import reverse


class AdminAllPermissionOrMeURLGetUPDMyself(permissions.BasePermission):
    """Кастомный пермишн для работы администратора и 'me' эндпоинта."""

    def has_permission(self, request, view):
        """Переопределяем стандартный метод has_permission."""
        if request.path == reverse('user-detail', kwargs={'username': 'me'}):
            # Если страница me, даем доступ
            return True
        # Если соответствующие эндпоинты users
        return bool(request.user.is_superuser or request.user.is_admin)


class AdminAllPermission(permissions.BasePermission):
    """
    Кастомный пермишн для работы администратора c небезопасными методами.
    """

    def has_permission(self, request, view):
        """Переопределяем стандартный метод has_permission."""
        return bool(request.user.is_superuser or request.user.is_admin)


class AdminAllOnlyAuthorPermission(permissions.BasePermission):
    """
    Кастомный пермишн для работы администратора
    автора объекта c небезопасными методами.
    """

    def has_object_permission(self, request, view, obj):
        """Переопределяем стандартный метод has_object_permission."""
        return bool(
            request.user.is_superuser
            or request.user.is_admin
            or obj.author == request.user
        )
