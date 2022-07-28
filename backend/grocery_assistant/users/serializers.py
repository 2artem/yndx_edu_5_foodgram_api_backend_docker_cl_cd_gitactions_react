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












class MySubscriptionsSerializer(serializers.ModelSerializer):
    '''Сериалайзер для вывода подписок пользователя.'''
    #email = serializers.ReadOnlyField(source="following.email")
    #id = serializers.ReadOnlyField(source="following.id")
    #username = serializers.ReadOnlyField(source="following.username")
    #first_name = serializers.ReadOnlyField(source="following.first_name")
    #last_name = serializers.ReadOnlyField(source="follower.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User #Follow
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
        return obj.following.count()
        author = obj.following
        #return Recipe.objects.filter(author=author).count()


    def get_recipes(self, obj):
        '''Рецепты пользователя.'''
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        #queryset = obj.following.recipe_set.all()
        #if limit is not None:
        #    queryset = Recipe.objects.filter(author=obj.user)[: int(limit)]
        #return RecipeShortSerializer(queryset, many=True).data
        return limit

''' def get_recipes(self, obj):
        request = self.context.get('request', )
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit', )
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeFollowSerializer(recipes, many=True, context=context).data'''



















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
