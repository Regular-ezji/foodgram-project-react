from django.contrib.auth import get_user_model
from django_filters import (CharFilter, FilterSet, ModelChoiceFilter,
                            ModelMultipleChoiceFilter)
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
