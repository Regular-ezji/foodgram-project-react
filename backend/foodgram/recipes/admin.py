from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorite_count'
    )
    search_fields = (
        'author',
        'name',
        'tags',
    )
    readonly_fields = (
        'favorite_count',
    )

    def favorite_count(self, obj):
        return obj.favorite_recipe.select_related('user').count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(RecipeIngredients)
