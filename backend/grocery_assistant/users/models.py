from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
#from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager

USER = 'user'
ADMIN = 'admin'


def username_validator_not_past_me(value):
    '''Проверка что username не равно me.'''
    message = (
        'В сервисе запрещено использовать '
        'значение '"'me'"' как имя пользователя.'
    )
    if value == 'me':
        raise ValidationError(message)


class User(AbstractBaseUser, PermissionsMixin):
    '''.'''
    username_validator = UnicodeUsernameValidator()
    # Роли
    ROLE = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    )
    role = models.CharField(
        'Роль',
        max_length=9,
        choices=ROLE,
        default=USER,
    )
    # Логин
    username = models.CharField(
        #_('username'),
        'Логин',
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator, username_validator_not_past_me],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # Имя
    first_name = models.CharField(
        _('first name'),
        max_length=150,
    )
    # Фамилия
    last_name = models.CharField(
        _('last name'),
        max_length=150,
    )
    # Электронная почта
    email = models.EmailField(
        _('email address'),
        max_length=254,
        unique=True)
    # Пароль
    password = models.CharField(
        _('password'),
        max_length=150,
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    @property
    def is_admin(self):
        return self.role == ADMIN

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
	    'last_name',
	    'password',
    ]

    

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
    
    def __str__(self):
        return self.email




'''

class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    # Роли
    ROLE = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор')
    )
    role = models.CharField(
        'Роль',
        max_length=9,
        choices=ROLE,
        default=USER,
    )
    # Логин
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        help_text=_(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator, username_validator_not_past_me],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # Имя
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=False,
        null=False,
    )
    # Фамилия
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=False,
        null=False,
    )
    # Электронная почта
    email = models.EmailField(
        _('email address'),
        max_length=254,
        blank=False,
        null=False,
        unique=True)
    # Пароль
    password = models.CharField(
        _('password'),
        max_length=150,
        blank=False,
        null=False,
    )
    #confirmation_code = models.CharField(
    #    'Код подтверждения email',
    #    max_length=150,
    #    blank=True,
    #   null=True,
    #)
    @property
    def is_admin(self):
        return self.role == ADMIN

    class Meta:
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username

'''

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписывающийся пользователь',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписываются',
    )

    class Meta:
        verbose_name = 'Связь автора и подписавшегося'
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships",
                fields=['user', 'following'],
            ),
            models.CheckConstraint(
                name="prevent_self_follow",
                check=~models.Q(user=models.F('following')),
            ),
        ]

    def __str__(self):
        return 'Пользователь {} подписан на {}'.format(
            self.user,
            self.following
        )
