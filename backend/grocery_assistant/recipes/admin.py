from django.contrib import admin
from .models import Ingredient
from .models import Tag, ShoppingUserList
from .models import Recipe, FavoritesRecipesUserList
from .models import RecipeTagRelationship, RecipeIngredientRelationship


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    ordering = ('pk',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
        'pub_date',
        'number_add_to_favorites',
    )
    filter_horizontal = ('ingredients', 'tags',)


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
        #'amount',
    )




class FavoritesRecipesUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'favorit_recipe',
    )




class ShoppingUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe_in_shoplist',
    )




admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTagRelationship, RecipeTagRelationshipAdmin)
admin.site.register(RecipeIngredientRelationship, RecipeIngredientRelationshipAdmin)
admin.site.register(FavoritesRecipesUserList, FavoritesRecipesUserListAdmin)
admin.site.register(ShoppingUserList, ShoppingUserListAdmin)

