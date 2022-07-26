from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404
# from reviews.models import Category, Genre, Title, Review, Comment
from .models import Recipe, Tag, Ingredient
from .models import  RecipeTagRelationship, RecipeIngredientRelationship, FavoritesRecipesUserList, ShoppingUserList
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




        # Достаем из запроса username и id произедения
        #title_id = self.context['request'].parser_context['kwargs']['title_id']
        #username = self.context['request'].user
        # Проверка на наличие в БД отзыва пользователя из запроса
        #if (Review.objects.filter(title_id=title_id, author=username).exists()
            #    and self.context['request'].method == 'POST'):


'''class MyField(serializers.Field):
    # При чтении данных ничего не меняем - просто возвращаем как есть
    def to_representation(self, value):
        return value
    # При записи код цвета конвертируется в его название
    def to_internal_value(self, data):
        # Доверяй, но проверяй
        #try:
            # Если имя цвета существует, то конвертируем код в название
            #data = webcolors.hex_to_name(data)
        #except ValueError:
            # Иначе возвращаем ошибку
            #raise serializers.ValidationError('Для этого цвета нет имени')
        # Возвращаем данные в новом формате
        return data'''


class RecipeIngredientRelationshipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredientRelationship
        #fields = '__all__'
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
    
    

class RecipeSerializer(serializers.ModelSerializer):
    # В моделе 'связи рецепта и его ингредиентов с их количествами' RecipeIngredientRelationship:
    # сериалайзер должен работать с полем рецепт
    ingredients = RecipeIngredientRelationshipSerializer(read_only=True, many=True, source='recipe')
    tags = TagSerializer(many=True) #read_only=True, 
    author = UserSerializer(read_only=True)#, many=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    # &&&&&&&&&&&&&&
    # 'image' =Base64ImageField()
    

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









class RecipeIngredientAmountCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientRelationship
        fields = (
            'id',
            'amount',
        )
    #def validate_id(self, value):
    #    if Ingredient.objects.filter(pk=value):
    #        raise serializers.ValidationError(f'Недопустимый первичный ключ \"{value}\" - объект не существует.')
    #    return value



class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientAmountCreateUpdateSerializer(
        many=True,
        source='recipe'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)


    class Meta:
        model = Recipe
        fields = (
            'tags', 
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def create(self, validated_data):
        # Уберем tag из словаря validated_data и сохраним его в tags
        ingredients = validated_data.pop('recipe')
        tags = validated_data.pop('tags')
        request = self.context.get('request')
        author = request.user
        recipe = Recipe.objects.create(
            author=author,
            **validated_data)
        # Для каждого тега из списка тегов
        for tag in tags:
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            RecipeTagRelationship.objects.create(
                tag=tag, recipe=recipe)
        # Для каждого тега из списка тегов
        for ingredient in ingredients:

            cur_id = ingredient['id']
            current_ingredient = Ingredient.objects.filter(id=cur_id).first()
            print(current_ingredient)
            if not current_ingredient:
                message = f'Недопустимый первичный ключ "{cur_id}" - объект не существует.'
                raise serializers.ValidationError(
                    #
                    {"ingredients": [ f"{message}"]}

                )
            amount = ingredient['amount']
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            RecipeIngredientRelationship.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount)
        return recipe








 