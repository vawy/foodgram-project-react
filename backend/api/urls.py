from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet, TagViewSet, IngredientViewSet, RecipeViewSet
)

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, 'users')
router_v1.register('tags', TagViewSet, 'tags')
router_v1.register('ingredients', IngredientViewSet, 'ingredients')
router_v1.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = (
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
