from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(models.Model):
    """
    Модель ингредиента.
    Уникальные поля: name, measurement_unit.
    """
    name = models.CharField(
        'Название ингредиента',
        max_length=100,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=50
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """
    Модель тега.
    Уникальные поля: name, color, slug.
    """
    name = models.CharField(
        'Название тега', max_length=100
    )
    color = models.CharField(
        'HEX-код',
        max_length=7,
        default='#'
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.
    Поле ingredients связывается с моделью Ingredient,
    через модель IngredientsAmount.
    Поле tags связывается с моделью Tag
    Сортировка по полю pub_date(дата публикации).
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название',
        max_length=256
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsAmount',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipe_images/%Y/%m/%d',
        default='static/images/DefaultCardImg.png'
    )
    text = models.TextField(
        'Описание', max_length=1000
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        null=False,
        validators=[
            MinValueValidator(
                1, message='Время должно быть больше/равно 1 минуты'
            )
        ],
        help_text='Укажите время в минутах',
        default=1
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:20]


class IngredientsAmount(models.Model):
    """
    Промежуточная модель между моделями Ingredient и Recipe,
    которая показывает кол-во ингредиентов в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиентов должно быть больше/равно 1'
            )
        ],
        default=1,
        null=False,
        help_text='Добавьте необходимое количество ингредиентов'
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


    def __str__(self):
        return (f'{self.recipe.name}: {self.ingredient.name} - '
                f'{self.amount}, {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """
    Модель избранных рецептов.
    Уникальные поля: user, recipe
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Список избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    Уникальные поля: user, recipes
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopcarts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopcarts'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
