from django.contrib.auth import get_user_model
from rest_framework import serializers
# from reviews.models import Category, Genre, Title, Review, Comment
from .models import Recipe, Tag, Ingredient
from rest_framework import status


User = get_user_model()


'''class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода информации."""
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(
        read_only=True,
    )
    genre = GenreSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitlesSerializerMethod(serializers.ModelSerializer):
    """Сериалайзер для изменения информации."""
    rating = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        slug_field='slug',
        required=True,
        many=False,
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        required=True,
        many=True,
        queryset=Genre.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        """
        Один пользователь может оставить
        только лишь один отзыв на произведение.
        """
        # Достаем из запроса username и id произедения
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        username = self.context['request'].user
        # Проверка на наличие в БД отзыва пользователя из запроса
        if (Review.objects.filter(title_id=title_id, author=username).exists()
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Вы уже оставляли свой отзыв к этому произведению.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
'''

class RecipeSerializer(serializers.ModelSerializer):
    '''author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        """
        Один пользователь может оставить
        только лишь один отзыв на произведение.
        """
        # Достаем из запроса username и id произедения
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        username = self.context['request'].user
        # Проверка на наличие в БД отзыва пользователя из запроса
        if (Review.objects.filter(title_id=title_id, author=username).exists()
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Вы уже оставляли свой отзыв к этому произведению.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data'''

    class Meta:
        model = Recipe
        # fields = ('id', 'text', 'author', 'score', 'pub_date')
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


 