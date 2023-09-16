from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response

from .serializers import ShortRecipeSerializer


def create_favorite_or_shopping_cart_obj(request, model, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        if model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                f'{str(model)}: Рецепт уже добавлен!',
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart = model(user=request.user, recipe=recipe)
        shopping_cart.save()
        data = ShortRecipeSerializer(recipe).data
        return Response(
            data,
            status=status.HTTP_201_CREATED
        )
    shopping_cart_recipe = get_object_or_404(
        model,
        user=request.user,
        recipe=recipe
    )
    shopping_cart_recipe.delete()
    return Response(
        f'{str(model)}: Рецепт был удален',
        status=status.HTTP_204_NO_CONTENT
    )
