from django.apps import AppConfig


class RecipeConfig(AppConfig):
    name = 'recipe'
    # Имя в админке
    verbose_name = 'Управление рецептами'
