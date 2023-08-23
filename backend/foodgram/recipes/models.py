from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название ингридиента',
        help_text='Название ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=150,
        blank=False,
        # choices=choices(???),
        verbose_name='Единица измерения',
        help_text='Единица измерения',
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Ключевое слово',
        help_text='Ключевое слово',
    )
    color = models.CharField(
        max_length=7,
        default='#ffffff',
        blank=False,
        verbose_name='HEX код цвета',
        help_text='HEX код цвета',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Сокращенное название тега для включения в URL-адрес',
        help_text='Сокращенное название тега для включения в URL-адрес',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipe_author',
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название рецепта',
        help_text='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='Фото блюда',
        help_text='Фотография блюда',
    )
    text = models.CharField(
        max_length=1000,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        help_text='Тег',
    )
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления, мин.',
        help_text='Время приготовления, мин.',
    )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='UsersFavorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        blank=False,
        on_delete=models.CASCADE,
        related_name='FavoriteRecipe',
        verbose_name='Рецепт',

    )

    def __str__(self):
        return (
            f'Избранный рецепт {self.recipe_id} у пользователя {self.user_id}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='UsersShoppingCart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        blank=False,
        on_delete=models.CASCADE,
        related_name='ShoppingCartRecipe',
        verbose_name='Рецепт',

    )

    def __str__(self):
        return (
            f'Рецепт {self.recipe_id} в корзине у пользователя {self.user_id}'
        )


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'
