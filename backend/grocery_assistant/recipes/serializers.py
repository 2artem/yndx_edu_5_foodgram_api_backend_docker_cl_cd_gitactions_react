from django.contrib.auth import get_user_model
from rest_framework import serializers
# from reviews.models import Category, Genre, Title, Review, Comment
from .models import Recipe, Tag, Ingredient, RecipeIngredientRelationship, FavoritesRecipesUserList, ShoppingUserList
from rest_framework import status
from users.serializers import UserSerializer
from django.contrib.auth.models import AnonymousUser

User = get_user_model()




class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
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





class RecipeIngredientRelationshipSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredientRelationship#Ingredient
        #fields = '__all__'
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
    
    def get_id(self, obj):
        return obj.ingredient.id
        
    def get_name(self, obj):
        return obj.ingredient.name
    
    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
    

class RecipeSerializer(serializers.ModelSerializer):
    # В моделе 'связи рецепта и его ингредиентов с их количествами' RecipeIngredientRelationship:
    # сериалайзер должен работать с полем рецепт
    ingredients = RecipeIngredientRelationshipSerializer(read_only=True, many=True, source='recipe')
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True, many=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    # &&&&&&&&&&&&&&
    # 'image' =Base64ImageField()
    

    # ингридиенты и теги обязательные к заполнению поля!!!!!!!!!!!!!!!!!!!!!! 6 обязательных полей


    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags', 
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        '''В избранном .'''
        user = self.context['request'].user
        # Если пользователь не аноним и подписка существует
        if (user != AnonymousUser()
            and FavoritesRecipesUserList.objects.filter(user=user ,favorit_recipe=obj.pk).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        '''В шоп листе .'''
        user = self.context['request'].user
        # Если пользователь не аноним и подписка существует
        if (user != AnonymousUser()
            and ShoppingUserList.objects.filter(user=user ,recipe_in_shoplist=obj.pk).exists()):
            return True
        return False













 