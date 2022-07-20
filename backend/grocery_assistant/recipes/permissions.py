from rest_framework import permissions


class AdminAllPermission(permissions.BasePermission):
    """
    Кастомный пермишн для работы администратора c небезопасными методами.
    """

    def has_permission(self, request, view):
        """Переопределяем стандартный метод has_permission."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_superuser or request.user.is_admin)


class AdminAllOnlyAuthorPermission(permissions.BasePermission):
    """
    Кастомный пермишн для работы администратора
    автора объекта c небезопасными методами.
    """

    def has_object_permission(self, request, view, obj):
        """Переопределяем стандартный метод has_object_permission."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user.is_superuser
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
