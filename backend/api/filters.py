from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import CharFilter, FilterSet, filters

from app.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по названию."""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value), output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору/тегу/подписке/наличию в списке покупок."""
    tags = CharFilter(field_name='tag__slug', lookup_expr='contains')
    author = CharFilter(field_name='recipe__author', lookup_expr='contains')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopcarts__user=self.request.user)
        return queryset
