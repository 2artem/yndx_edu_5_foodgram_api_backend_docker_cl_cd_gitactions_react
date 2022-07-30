'''
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
'''

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
#from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Follow

#User = get_user_model()
from .models import User

class CustomUserAdmin(UserAdmin):
    '''Кастомная админка.'''
    #add_form = CustomUserCreationForm
    #form = CustomUserChangeForm
    model = User
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'is_staff',
        'is_superuser',
    )
    #list_filter = ('email', 'is_staff', 'is_active',)
    '''fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )'''
    search_fields = ('email',)
    ordering = ('email',)
    empty_value_display = 'NULL'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, CustomUserAdmin)


