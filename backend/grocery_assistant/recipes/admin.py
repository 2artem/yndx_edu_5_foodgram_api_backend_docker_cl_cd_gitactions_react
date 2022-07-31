from django.contrib import admin

from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     RecipeIngredientRelationship, RecipeTagRelationship,
                     ShoppingUserList, Tag)


class RecipeInline(admin.TabularInline):
    model = RecipeTagRelationship


class RecipeAdmin(admin.ModelAdmin):
    '''
    Администрирование модели рецепта, вывод названия и автора.
    Фильтр по автору, названию, тегам.
    '''
    list_display = (
        'pk',
        'author',
        'name',
    )
    # фильтрация
    list_filter = ('author', 'name', 'tags',)
    inlines = [RecipeInline, ]
    # фильтрация по тегу

    class Meta:
        model = Recipe


class IngredientAdmin(admin.ModelAdmin):
    '''Администрирование модели ингредиента, с фильтром по названию.'''
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    ordering = ('pk',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('name',)
    # Добавляем возможность фильтрации по названию
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'color'
    )


class RecipeTagRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'tag',
        'recipe',
    )


class RecipeIngredientRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
    )


class FavoritesRecipesUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


class ShoppingUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTagRelationship, RecipeTagRelationshipAdmin)
admin.site.register(
    RecipeIngredientRelationship,
    RecipeIngredientRelationshipAdmin
)
admin.site.register(FavoritesRecipesUserList, FavoritesRecipesUserListAdmin)
admin.site.register(ShoppingUserList, ShoppingUserListAdmin)
