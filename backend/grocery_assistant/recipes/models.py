import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

User = get_user_model()


def hex_field_validator(value):
    '''Проверка что содержимое поля в формате HEX.'''
    message = (
        'Введите цвет в формате HEX.'
    )
    if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise ValidationError(message)


class Ingredient(models.Model):
    '''Модель ингредиента.'''
    name = models.CharField(
        max_length=200,
        unique=False,
        db_index=True,
        verbose_name='название ингредиента',
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
        verbose_name='название тега',
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
    cooking_time = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='время приготовления в минутах',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимальное время приготовления - 1 минута.')
        ],
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
        verbose_name='название',
    )
    image = models.ImageField(
        blank=False,
        null=False,
        verbose_name='картинка',
        upload_to='recipe',
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
        verbose_name='тег',
        through='RecipeTagRelationship'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return '{}.. - ({}..)'.format(
            self.name[:15],
            self.text[:15]
        )


class RecipeTagRelationship(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Связь тега c рецептом'
        verbose_name_plural = 'Связи тегов c рецептами'
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_tag_recipe',
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
        related_name='ingredient_in_recipe',
        verbose_name='рецепт',
    )
    amount = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='количество ингредиента в рецепте',
        validators=[MinValueValidator(
            limit_value=1,
            message='Количество должно быть больше 0.')
        ],
    )

    class Meta:
        verbose_name = 'Связь ингредиента c рецептом'
        verbose_name_plural = 'Связи ингредиентов c рецептами'
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_ingredient_recipe',
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
        related_name='favorit_recipe',
        verbose_name='Пользователь, имеющий избранные рецепты',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorit_recipe',
        verbose_name='Избранный рецепт определенного пользователя',
    )

    class Meta:
        verbose_name = 'Связь избранного рецепта с пользователем'
        verbose_name_plural = 'Связи избранных рецептов с пользователями'
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_user_fav_recipe',
                fields=['user', 'recipe'],
            ),
        ]

    def __str__(self):
        return 'У {} в избранном рецепт: {}'.format(
            self.user,
            self.recipe
        )


class ShoppingUserList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_in_shoplist',
        verbose_name='Пользователь, имеющий рецепт в Списке покупок',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_shoplist',
        verbose_name='Рецепт из списка покупок пользователя',
    )

    class Meta:
        verbose_name = 'Связь списка покупок (рецепта с пользователем)'
        verbose_name_plural = (
            'Связи списка покупок '
            + '(рецептов с пользователями)'
        )
        constraints = [
            models.UniqueConstraint(
                name='unique_relationships_user_shoplist',
                fields=['user', 'recipe'],
            ),
        ]

    def __str__(self):
        return 'У {} в Списке покупок рецепт: {}'.format(
            self.user,
            self.recipe
        )
