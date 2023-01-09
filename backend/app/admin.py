from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart, IngredientsAmount
)


class IngredientsAmountInline(admin.TabularInline):
    model = IngredientsAmount
    extra = 1

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username', 'author__last_name',
                     'author__first_name', 'tags__name')
    readonly_fields = ('favorite_count', 'shopping_count')
    filter_vertical = ('tags', 'ingredients')
    inlines = (IngredientsAmountInline,)

    def favorite_count(self, obj):
        return obj.favorites.count()

    def shopping_count(self, obj):
        return obj.shopcarts.count()

    favorite_count.short_description = 'В избранном'
    shopping_count.short_description = 'В списке покупок'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)

class IngredientsAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsAmount, IngredientsAmountAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)