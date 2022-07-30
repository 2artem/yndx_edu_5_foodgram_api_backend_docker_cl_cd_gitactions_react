from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
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
    ingredients = RecipeIngredientRelationshipSerializer(read_only=True, many=True, source='recipe_for_ingredient')
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
            and FavoritesRecipesUserList.objects.filter(user=user ,recipe=obj.pk).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        '''В шоп листе .'''
        user = self.context['request'].user
        # Если пользователь не аноним и подписка существует
        if (user != AnonymousUser()
            and ShoppingUserList.objects.filter(user=user ,recipe=obj.pk).exists()):
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

def create_relationship_tag_recipe(tags, recipe):
    '''Наполение связующей таблицы тега и рецепта.'''
    for tag in tags:
        RecipeTagRelationship.objects.create(tag=tag, recipe=recipe)

def create_relationship_ingredient_recipe(ingredients, recipe):
    for ingredient in ingredients:
        cur_id = ingredient['id']
        current_ingredient = Ingredient.objects.filter(id=cur_id).first()
        if not current_ingredient:
            message = f'Недопустимый первичный ключ "{cur_id}" - объект не существует.'
            raise serializers.ValidationError(
                {"ingredients": [ f"{message}"]}
            )
        amount = ingredient['amount']
        RecipeIngredientRelationship.objects.create(
            ingredient=current_ingredient,
            recipe=recipe,
            amount=amount
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''Сериалайзер, производящий запись или обновление рецепта.'''
    ingredients = RecipeIngredientAmountCreateUpdateSerializer(
        many=True,
        source='recipe_for_ingredient'
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
        '''На вывод возвращаем рецепт через другой сериалайзер.'''
        return RecipeSerializer(instance, context=self.context).data
    
    def validate(self, data):
        '''Проверяем уникальность введенных ингридиентов и тегов в рецепте.'''
        # Проверим теги в запросе на уникальность
        tags = data.get('tags')
        all_tags_request = len(tags)
        uniq_tags = set()
        for tag in tags:
            uniq_tags.add(tag.pk)
        if len(uniq_tags) != all_tags_request:
            raise serializers.ValidationError(
                {"tags": ["Теги должны быть уникальными."]}
            )
        # Проверим ингридиенты в запросе на уникальность
        # и то, что количество не меньше 0
        ingredients = data.get('recipe_for_ingredient')
        all_ingredients_request = len(ingredients)
        uniq_ingredients = set()
        list_null_amount = list()
        for ingredient in ingredients:
            id = ingredient['id']
            amount = ingredient['amount']
            # если меньше нуля
            if amount <= 0:
                list_null_amount.append(
                    (
                        f'Количество \"amount\" для ингридиента c "id" = {id}'
                        +f' должно быть больше 0, у Вас {amount}.'
                    )
                )
            uniq_ingredients.add(id)
        if len(uniq_ingredients) != all_ingredients_request:
            raise serializers.ValidationError(
                {"ingredients": ["Ингридиенты должны быть уникальными."]}
            )
        if list_null_amount:
            raise serializers.ValidationError(
                {"ingredients": list_null_amount}
            )
        return data



    def create(self, validated_data):
        '''Переопределение создания рецепта.'''
        try:
            with transaction.atomic():
                # заберем ингредиенты и теги из валидированных входных данных
                ingredients = validated_data.pop('recipe_for_ingredient')
                tags = validated_data.pop('tags')
                author = self.context.get('request').user
                recipe = Recipe.objects.create(
                    author=author,
                    **validated_data
                )
                # создадим отношения между тегами и рецептами в Связующей таблице
                create_relationship_tag_recipe(tags, recipe)
                # создадим отношения между ингридиентами и рецептами в Связующей таблице,
                # если такие есть в БД
                create_relationship_ingredient_recipe(ingredients, recipe)
        except IntegrityError:
            raise serializers.ValidationError(validated_data, status.HTTP_400_BAD_REQUEST)
        return recipe


    def update(self, instance, validated_data):
        '''Переопределение обновления рецепта.'''


        # автора беру из токена или из Инстанс???
        author = self.context.get('request').user

    
        try:
            with transaction.atomic():
                # достаем редактируемый рецепт
                current_obj_recipe = get_object_or_404(Recipe, id=instance.pk)
                # чистим связи рецепта с тегами
                records_tag_recipe = RecipeTagRelationship.objects.filter(recipe=current_obj_recipe)
                for record in records_tag_recipe:
                   record.delete()
                # чистим свзяи с ингридиентами
                records_ingredient_recipe = RecipeIngredientRelationship.objects.filter(recipe=current_obj_recipe)
                for record in records_ingredient_recipe:
                    record.delete()
                # Входные данные
                ingredients = validated_data.pop('recipe_for_ingredient')
                tags = validated_data.pop('tags')
                # создадим отношения между тегами и рецептами в Связующей таблице
                create_relationship_tag_recipe(tags, current_obj_recipe)
                # создадим отношения между ингридиентами и рецептами в Связующей таблице,
                # если такие есть в БД
                create_relationship_ingredient_recipe(ingredients, current_obj_recipe)
                instance.image = validated_data.get('image', instance.image)
                instance.name = validated_data.get('name', instance.name)
                instance.text = validated_data.get('text', instance.text)
                instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
                instance.save()
        except IntegrityError:
            raise serializers.ValidationError(validated_data, status.HTTP_400_BAD_REQUEST)
        return instance





        










 