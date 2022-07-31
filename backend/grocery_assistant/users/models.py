from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


def username_validator_not_past_me(value):
    '''Проверка что username не равно me.'''
    message = (
        'В сервисе запрещено использовать '
        'значение \"me\" как имя пользователя.'
    )
    if value == 'me':
        raise ValidationError(message)


class User(AbstractBaseUser, PermissionsMixin):
    '''Кастомная модель Юзера.'''
    username_validator = UnicodeUsernameValidator()
    # Логин
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator, username_validator_not_past_me],
        error_messages={
            'unique': _('A user with that username already exists.'),
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
        validators=[validate_password],
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

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


class Follow(models.Model):
    '''Модель связующей таблицы подписок пользователей.'''
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
        verbose_name_plural = (
            'Связи авторов и подписавшихся'
            + 'на них пользователей'
        )
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_user_following',
                fields=['user', 'following'],
            ),
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        ]

    def __str__(self):
        return 'Пользователь {} подписан на {}'.format(
            self.user,
            self.following
        )
