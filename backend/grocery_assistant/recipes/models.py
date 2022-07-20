from django.core.validators import validate_slug
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from .validators import check_value_year_valid

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='название',
        )
    # Болванка
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения',
    )

    class Meta:
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
        validators=[validate_slug]
    )
    # Болванка для цвета
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='цвет',
    )

    class Meta:
        ordering = ['slug']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    '''Модель рецепта.'''
    cooking_time = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
        verbose_name='время приготовления',
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
        related_name='recipes',
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )
    name = models.CharField(
        max_length=256,
        # unique=True,
        blank=False,
        null=False,
        verbose_name='название'
    )
    image = models.TextField(
        max_length=1000,
        blank=False,
        null=False,
        verbose_name='картинка',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        # on_delete=models.SET_NULL,
        blank=False,
        db_index=True,
        related_name='ingredients',
        verbose_name='ингридиент'
    )
    tags = models.ManyToManyField(
        Tag,
        # on_delete=models.SET_NULL,
        blank=False,
        db_index=True,
        related_name='tags',
        verbose_name='тег'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = "рецепты"
        constraints = [
            models.UniqueConstraint(
                name="unique_relationships",
                fields=['author', 'name'],
            ),
        ]

    def __str__(self):
        return self.text[:15]
