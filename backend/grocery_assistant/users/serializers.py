from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow

User = get_user_model()
username_validator = UnicodeUsernameValidator()


class SetPasswordSerializer(serializers.Serializer):
    '''Сериалайзер установки пароля.'''
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


def user_is_subscribed(self, obj):
    '''Подписан ли текущий пользователь на другого пользователя.'''
    user = self.context['request'].user
    # Если пользователь не аноним и подписка существует
    if (user.is_anonymous is not True
            and Follow.objects.filter(user=user, following=obj.pk).exists()):
        return True
    return False


class UserSerializer(serializers.ModelSerializer):
    '''Сериалайзер для пользователя.'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        '''Подписан ли текущий пользователь на другого пользователя.'''
        return user_is_subscribed(self, obj)


class NewUserSerializer(serializers.ModelSerializer):
    '''Сериалайзер для нового пользователя.'''

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def validate_password(self, value):
        '''Проверка пароля.'''
        return make_password(value)


class SubRecipeSerializer(serializers.ModelSerializer):
    '''Сериалайзер для вывода полей рецепта в подписках.'''
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    '''Сериалайзер для вывода подписок пользователя.'''
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        '''Подписан ли текущий пользователь на другого пользователя.'''
        return user_is_subscribed(self, obj)

    def get_recipes_count(self, obj):
        '''Общее количество рецептов пользователя.'''
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        '''Получить рецепты пользователя.'''
        # передан ли параметр recipes_limit,
        # отвечающий за количество объектов внутри поля
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        # водим рецепты интересующего пользователя,
        # отталкиваясь от параметра recipes_limit, если он есть
        interes_user = obj
        if recipes_limit:
            return SubRecipeSerializer(Recipe.objects.filter(
                author=interes_user)[:int(recipes_limit)],
                many=True).data
        return SubRecipeSerializer(
            Recipe.objects.filter(author=interes_user),
            many=True).data


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели Follow.'''
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Подписка на самого себя невозможна.'
            )
        return data

    class Meta:
        fields = ('id', 'user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Подписка уже существует'
            )
        ]
