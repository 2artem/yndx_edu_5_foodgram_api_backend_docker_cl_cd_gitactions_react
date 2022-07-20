from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import username_validator_not_past_me
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.validators import UniqueTogetherValidator
from .models import Follow
from django.contrib.auth.models import AnonymousUser

User = get_user_model()
username_validator = UnicodeUsernameValidator()

class UserAuthSerializer(serializers.Serializer):
    """Сериалайзер для регистрации пользователя."""
    email = serializers.EmailField(required=True)
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[username_validator, username_validator_not_past_me],
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    password = serializers.CharField(
        max_length=150,
        required=True,
    )



class UserConfirmationCodeSerializer(serializers.Serializer):
    """Сериалайзер для выдачи кода пользователю."""
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[username_validator, username_validator_not_past_me],
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True,
    )


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
        # Достаем из запроса username и id произедения
        # title_id = self.context['request'].parser_context['kwargs']['title_id']
        return str(self.context['request'].user) == 'AnonymousUser'


class NewUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )

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
