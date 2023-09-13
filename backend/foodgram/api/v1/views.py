from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateListDestroyViewSet, ListViewSet, RetrieveListViewSet
from .serializers import (ChangePasswordSerializer, FollowSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          SignInSerializer, TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    '''Вьюсет для работы с пользователями'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = (AllowAny, )

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', ],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        if not check_password(
            serializer.validated_data['current_password'],
            current_user.password
        ):
            message = {'message': 'Неверный пароль!'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        current_user.set_password(serializer._validated_data['new_password'])
        current_user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    '''Вью функция для получения токена авторизации'''
    serializer = SignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    user = get_object_or_404(User, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {'auth_token': str(token)},
        status=status.HTTP_200_OK
    )


class TagViewSet(RetrieveListViewSet):
    '''Вьюсет для работы с тегами'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(RetrieveListViewSet):
    '''Вьюсет для работы с ингредиентами'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для работы с рецептами'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже добавлен в избранное!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite(user=request.user, recipe=recipe)
            favorite.save()
            data = ShortRecipeSerializer(recipe).data
            return Response(
                data,
                status=status.HTTP_201_CREATED
            )
        favorite_recipe = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        )
        favorite_recipe.delete()
        return Response(
            'Рецепт был удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже добавлен в корзину!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart = ShoppingCart(user=request.user, recipe=recipe)
            shopping_cart.save()
            data = ShortRecipeSerializer(recipe).data
            return Response(
                data,
                status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe
        )
        shopping_cart_recipe.delete()
        return Response(
            'Рецепт был удален из корзины',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get', ])
    def download_shopping_cart(self, request):
        filename = 'shopping_list.txt'
        user = request.user
        ingredients = RecipeIngredients.objects.filter(
            recipe__ShoppingCartRecipe__user=user
        ).values(
            'ingredient'
        ).annotate(
            total_amount=Sum('amount')
        ).values_list(
            'ingredient__name', 'total_amount', 'ingredient__measurement_unit'
        )
        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += '{} - {} {}. \n'.format(*ingredient)

        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response


class FollowViewSet(CreateListDestroyViewSet):
    '''Вьюсет для работы с подписками'''
    permission_classes = (IsAuthenticated, )
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))

        serializer.save(
            user=self.request.user,
            author=author
        )

    def delete(self, request, id):
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        follow = get_object_or_404(
            Follow,
            user=request.user,
            author=author
        )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsListViewSet(ListViewSet):
    '''Вьюсет для получения всех подписок пользователя'''
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user_id=request.user.id).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
