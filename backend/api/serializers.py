from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from base64 import b64decode

from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from app.models import (
    Ingredient, Tag, Recipe, IngredientsAmount, Favorite, ShoppingCart
)
from users.models import Follow, CustomUser

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения сведений о рецепте"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='photo.' + ext)
        return super().to_internal_value(data)

class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = CustomUser
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления подписки, просмотра подписок."""
    recipes = ShortRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('__all__',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)

class IngredientsAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов с их кол-вом."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('__all__',)

    def get_ingredients(self, obj):
        queryset = IngredientsAmount.objects.filter(recipe=obj)
        return IngredientsAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shopcarts.filter(user=user).exists()

class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления/удаления рецепта."""
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        amount_message = 'Количество ингредиента должно быть больше или равно 1.'
        ingredient_message = 'Ингредиенты должны быть уникальными.'
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    {'ingredients': ingredient_message}
                )
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if not int(amount) >= 1:
                raise serializers.ValidationError(
                    {'amount': amount_message}
                )

        if not data['tags']:
            raise serializers.ValidationError(
                {'tags': 'Выберите хотя бы один тэг.'}
            )
        tag_list = []
        for tag in data['tags']:
            if tag in tag_list:
                raise serializers.ValidationError(
                    {'tags': 'Тэги должны быть уникальными.'}
                )
            tag_list.append(tag)

        if not int(data['cooking_time']):
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть больше или равно 1'}
            )
        return data


    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time', recipe.cooking_time)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)

        recipe.save()
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта в/из избранное(ого)."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {'error': 'Этот рецепт уже добавлен.'}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteRecipeSerializer):
    """Сериализатор для добавления/удаления рецепта в список покупок."""
    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingCart
