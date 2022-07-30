from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import username_validator_not_past_me
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import UniqueTogetherValidator
from .models import Follow
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from recipes.models import Recipe



User = get_user_model()
username_validator = UnicodeUsernameValidator()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    #class Meta:
     #   validators = [
     #       validate_new_password
     #   ]

def user_is_subscribed(self, obj):
    '''Подписан ли текущий пользователь на другого пользователя.'''
    user = self.context['request'].user
    # Если пользователь не аноним и подписка существует
    if (user != AnonymousUser()
        and Follow.objects.filter(user=user ,following=obj.pk).exists()):
        return True
    return False


class UserSerializer(serializers.ModelSerializer):
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
        return make_password(value)









class SubRecipeSerializer(serializers.ModelSerializer):
    '''.'''

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
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        '''Подписан ли текущий пользователь на другого пользователя.'''
        return user_is_subscribed(self, obj)

    def get_recipes_count(self, obj):
        '''Общее количество рецептов пользователя.'''

        return Recipe.objects.filter(
            author=self.context['interes_user']
            ).count()

    def get_recipes(self, obj):
        '''Рецепты пользователя.'''
        # передан ли параметр recipes_limit, отвечающий за количество объектов внутри поля
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        # водим рецепты интересующего пользователя,
        # отталкиваясь от параметра recipes_limit, если он есть
        interes_user= self.context['interes_user']
        if recipes_limit:
            return SubRecipeSerializer(
                Recipe.objects.filter(author=interes_user)[:int(recipes_limit)],
                many=True).data
        return SubRecipeSerializer(
            Recipe.objects.filter(author=interes_user),
            many=True).data




class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
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
