from django.core.validators import validate_slug
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from .validators import check_value_year_valid
from django.core.exceptions import ValidationError
import re


User = get_user_model()

def cooking_time_validator_at_least_1_minute(value):
    '''Проверка что .'''
    message = (
        'Время приготовления не может быть меньше 1 минуты.'
    )
    if value < 1:
        raise ValidationError(message)

def amount_above_zero_validator(value):
    '''Проверка что .'''
    message = (
        'Количество должно быть больше 0.'
    )
    if value <= 0:
        raise ValidationError(message)

def hex_field_validator(value):
    '''Проверка что .'''
    message = (
        'Введите цвет в формате HEX.'
    )
    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(message)




class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=False,
        db_index=True,
        verbose_name='название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='название',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='slug',
        validators=[validate_slug]
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX цвет',
        validators=[hex_field_validator]
    )

    class Meta:
        ordering = ['slug']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.slug



class Recipe(models.Model):
    '''Модель рецепта.'''
    cooking_time = models.IntegerField(
        blank=False,
        null=False,
        verbose_name='время приготовления в минутах',
        validators=[cooking_time_validator_at_least_1_minute],
    )
    text = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
        verbose_name='текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        #related_name='recipes',
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='название'
    )
    # Картинка, закодированная в Base64 при создании
    image = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
        verbose_name='картинка',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        db_index=True,
        related_name='ingredients_recipes',
        verbose_name='ингридиент',
        through='RecipeIngredientRelationship'
    )
    tags = models.ManyToManyField(
        Tag,
        db_index=True,
        #related_name='tag',
        verbose_name='тег',
        through='RecipeTagRelationship'
    )
    # КОЛИЧЕСТВО -ОБЩЕЕ ЧИСТО ДОБАВЛЕНИЙ РЕЦЕПТРА В ИЗБРАННОЕ (думаю отдельными людьми) Запоминать кто уже добавлял..
    number_add_to_favorites = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='общее число добавлений рецепта в избранное',
        validators=[cooking_time_validator_at_least_1_minute],
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = "рецепты"
        #constraints = [
        #    models.UniqueConstraint(
        #        name="unique_relationships1",
        #        fields=['author', 'name'],
        #    ),
        #]

    def __str__(self):
        return '{}.. - ({}..)'.format(
            self.name[:15],
            self.text[:15]
        )
    







class RecipeTagRelationship(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        #related_name='tag',
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        #related_name='recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Связь тега и рецепта'
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships2",
                fields=['tag', 'recipe'],
            ),
        ]

    def __str__(self):
        return 'Тег {} в рецепте {}'.format(
            self.tag,
            self.recipe
        )


class RecipeIngredientRelationship(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='ингридиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_for_ingredient',
        verbose_name='рецепт',
    )
    amount = models.IntegerField(
        blank=False,
        null=False,
        verbose_name='количество',
        validators=[amount_above_zero_validator],
    )

    class Meta:
        verbose_name = 'Связь ингредиента и рецепта'
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships3",
                fields=['ingredient', 'recipe'],
            ),
        ]

    def __str__(self):
        return 'Ингридиент {} в рецепте {}'.format(
            self.ingredient,
            self.recipe
        )






class FavoritesRecipesUserList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user1',
        verbose_name='Пользователь, имеющий избранные рецепты',
    )
    favorit_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorit_recipe',
        verbose_name='Избранный рецепт определенного пользователя',
    )

    class Meta:
        verbose_name = 'Связи пользователя с его избранными рецептами'
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships4",
                fields=['user', 'favorit_recipe'],
            ),
        ]

    def __str__(self):
        return 'У {} в избранном рецепт: {}'.format(
            self.user,
            self.favorit_recipe
        )


class ShoppingUserList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        #related_name='user',
        verbose_name='Пользователь, имеющий рецепт в Списке покупок',
    )
    recipe_in_shoplist = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shoplist',
        verbose_name='Рецепт из списка покупок пользователя',
    )

    class Meta:
        verbose_name = 'Рецепты пользователя добавленные в Список покупок'
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships5",
                fields=['user', 'recipe_in_shoplist'],
            ),
        ]

    def __str__(self):
        return 'У {} в Списке покупок рецепт: {}'.format(
            self.user,
            self.recipe_in_shoplist
        )
        # return f'{self.achievement} {self.cat}'





