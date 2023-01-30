from datetime import datetime

from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from app.models import Ingredient, IngredientsAmount, Recipe, Tag
from users.models import CustomUser, Follow

from .filters import IngredientFilter, RecipeFilter
from .paginations import LimitPagination
from .permissions import AuthorStaffOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, TagSerializer)


class UsersViewSet(UserViewSet):
    """
    Вьюсет для работы с пользователями.
    Обработка запросов на создание/получение пользователей.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    add_serializer = FollowSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        authors = CustomUser.objects.filter(followings__user=user)
        page = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=id)
        subscription = Follow.objects.filter(
            user=user, author=author
        )

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(author, context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

            # if subscription.exists():
            #     subscription.delete()
            #     return Response(status=status.HTTP_204_NO_CONTENT)
            # return Response(
            #     {'error': 'Вы не подписаны на этого пользователя'},
            #     status=status.HTTP_400_BAD_REQUEST
            # )


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения ингердиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов"""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorStaffOrReadOnly]
    pagination_class = LimitPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        model_obj = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not model_obj.exists():
                return Response({'error': 'Этого рецепта нет в избранном.'},
                                status=status.HTTP_400_BAD_REQUEST)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

            # if model_obj.exists():
            #     model_obj.delete()
            #     return Response(status=status.HTTP_204_NO_CONTENT)
            # return Response({'error': 'Этого рецепта нет в избранном.'},
            #                 status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.action_post_delete(pk, FavoriteRecipeSerializer)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.action_post_delete(pk, ShoppingCartSerializer)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated], pagination_class=None)
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopcarts.exists():
            return Response({'error': 'Список покупок пуст'},
                            status=status.HTTP_204_NO_CONTENT)
        ingredients = IngredientsAmount.objects.filter(
            recipe__shopcarts__user=user
        ).values(
            ingredients=F('ingredient__name'),
            measure=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок\n\n{user.username}\n'
            f'{datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredients"]} - {ing["amount"]}, {ing["measure"]}\n'
            )
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
