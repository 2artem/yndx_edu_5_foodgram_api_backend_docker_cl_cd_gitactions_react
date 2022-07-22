from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import username_validator_not_past_me
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import UniqueTogetherValidator
from .models import Follow
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password



User = get_user_model()
username_validator = UnicodeUsernameValidator()

class UserGetTokenSerializer(serializers.Serializer):
    """Сериалайзер для выдачи токена пользователю."""
    password = serializers.CharField(
        max_length=150,
        required=True, 
    )
    email = serializers.EmailField(required=True)


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
        user = self.context['request'].user
        # Если пользователь не аноним и подписка существует
        if (user != AnonymousUser()
            and Follow.objects.filter(user=user ,following=obj.pk).exists()):
            return True
        return False


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
