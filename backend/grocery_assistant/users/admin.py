from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Кастомная Админка"""
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'role',
        'is_staff',
        'is_superuser',
    )
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('username',)
    empty_value_display = 'NULL'
    # Добавляем возможность фильтрации по дате
    # list_filter = ('pub_date',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)