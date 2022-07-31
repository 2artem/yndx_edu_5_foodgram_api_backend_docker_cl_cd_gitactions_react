from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Follow

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    '''Кастомная админка.'''
    model = User
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('email',)
    ordering = ('email',)
    empty_value_display = 'NULL'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, CustomUserAdmin)
