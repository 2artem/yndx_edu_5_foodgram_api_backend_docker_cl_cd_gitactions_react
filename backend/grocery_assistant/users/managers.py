from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    '''
    Кастомный диспетчер пользовательских моделей пользователей, в котором
    электронная почта является уникальным идентификатором для аутентификации,
    а не именами пользователей.
    '''
    def create_user(
            self,
            email,
            password,
            username,
            first_name,
            last_name,
            **extra_fields):
        '''
        Создать и сохранить пользователя с указанным адресом
        электронной почты и паролем.
        '''
        if not email:
            raise ValueError(_('The Email must be set'))
        user = self.model(
            email=self.normalize_email(email),
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self,
            email,
            password,
            username,
            first_name,
            last_name,
            **extra_fields):
        '''
        Создайть и сохранить суперпользователя с указанным адресом
        электронной почты и паролем.
        '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
