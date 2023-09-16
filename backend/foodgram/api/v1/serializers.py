from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User

from .validators import username_validator


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с пользователями'''
    username = serializers.CharField(
        max_length=150,
        validators=[username_validator],
    )
    password = serializers.CharField(
        max_length=150,
        write_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed', )

    def validate(self, data):
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        if 'password' in data:
            password = make_password(data['password'])
            data['password'] = password
            return data
        return data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=obj
        ).exists()

    def to_representation(self, instance):
        request = self.context.get('request')
        if request.method == 'POST' and request.path == '/api/users/':
            self.fields.pop('is_subscribed')
        return super().to_representation(instance)


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с ингредиентами'''
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с тегами'''
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'name',
            'color',
            'slug',
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с ингредиентами рецепта'''
    amount = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount',
            'recipe',
        )


class GetRecipeIngredientsSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения ингредиентов рецепта'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount',
            'measurement_unit',
            'name',
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения рецептов'''
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous or not request:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous or not request:
            return False
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredients.objects.filter(recipe=obj)
        return GetRecipeIngredientsSerializer(
            recipe_ingredients,
            many=True
        ).data

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


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с рецептами'''
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Один из ингредиентов повторяется несколько раз!'
            )
        tags = self.initial_data.get('tags')
        tags_list = [tag for tag in tags]
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError(
                'Один из тегов повторяется несколько раз!'
            )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        list_generation_data = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(list_generation_data)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in self.validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        if 'ingredients' in self.validated_data:
            ingredients_data = validated_data.pop('ingredients')
            with transaction.atomic():
                amount_set = RecipeIngredients.objects.filter(
                    recipe__id=instance.id)
                amount_set.delete()
                bulk_create_data = (
                    RecipeIngredients(
                        recipe=instance,
                        ingredient=ingredient_data['ingredient'],
                        amount=ingredient_data['amount'])
                    for ingredient_data in ingredients_data
                )
                RecipeIngredients.objects.bulk_create(bulk_create_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingredients')
        self.fields.pop('tags')
        representation = super().to_representation(instance)
        representation['ingredients'] = GetRecipeIngredientsSerializer(
            RecipeIngredients.objects.filter(recipe=instance),
            many=True
        ).data
        representation['tags'] = TagSerializer(
            instance.tags,
            many=True
        ).data
        return representation


class SignInSerializer(serializers.Serializer):
    '''Сериализатор для получения токена авторизации'''
    password = serializers.CharField(
        max_length=150,
        required=True,
    )
    email = serializers.CharField(
        max_length=150,
        required=True,
    )

    def validate(self, data):
        user = get_object_or_404(User, email=data['email'])
        if check_password(data['password'], user.password):
            return data
        raise serializers.ValidationError(
            {'password': 'Неверный пароль'}
        )


class ChangePasswordSerializer(serializers.Serializer):
    '''Сериализатор для смены пароля'''
    new_password = serializers.CharField(
        max_length=150,
        required=True,
    )

    current_password = serializers.CharField(
        max_length=150,
        required=True,
    )

    def validate(self, data):
        if 'password' in data:
            password = make_password(data['password'])
            data['password'] = password
            return data
        return data


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с подписками'''
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def validate(self, data):
        request = self.context.get('request')
        user_id = request.user.id
        author_id = int(request.parser_context['kwargs']['id'])
        if Follow.objects.filter(
            user=user_id,
            author=author_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя!'
            )
        if user_id == author_id:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя'
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для получения краткой информации о рецепте'''
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
