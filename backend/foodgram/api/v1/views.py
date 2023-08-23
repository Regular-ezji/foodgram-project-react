from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from djoser import utils
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from users.models import User

from .mixins import (CreateDestroyViewSet, CreateListDestroyViewSet,
                     CreateListRetriveViewSet, CreateViewSet, ListViewSet,
                     RetrieveListViewSet)
from .serializers import (ChangePasswordSerializer, FavoriteSerializer,
                          FollowSerializer, GetRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SignInSerializer,
                          SubscriptionsListSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    permission_classes = (AllowAny, )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
            methods=['post'],
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
            message = 'Неверный пароль!'
            return Response(message, status=status.HTTP_204_NO_CONTENT)
        current_user.set_password(
            serializer._validated_data['new_password']
            )
        current_user.save()
        message = 'Пароль успешно изменен!'
        return Response(message, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = SignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    user = get_object_or_404(User, email=email)
    token = AccessToken.for_user(user)
    return Response(
        {'token': str(token)},
        status=status.HTTP_200_OK
    )


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            shop = get_object_or_404(ShoppingCart, user=self.request.user)
            print(shop, ' МАТЬ ЕБААААААААААААААААААЛ')
            return GetRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            print(recipe)
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
            data = FavoriteSerializer(recipe).data
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
            data = ShoppingCartSerializer(recipe).data
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

    @action(detail=True, methods=['post'])
    def download_shopping_cart(self, request):
        filename = 'shopping_list.txt'
        pass


class FollowViewSet(CreateListDestroyViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionsListViewSet(ListViewSet):
    serializer_class = SubscriptionsListSerializer                   
    permission_classes = (IsAuthenticated, )

    # def get_object(self):
    #     user_id = self.get['user_id']
    #     user = get_object_or_404(CustomUser, user_id)


# class LogoutViewSet(CreateViewSet):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         access_token = request.data.get('token')
#         if not access_token:
#             return Response({'detail': 'Token is required.'}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             token = AccessToken(access_token)
#             token.blacklist()
#         except:
#             return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(
#             methods=['post'],
#             detail=False,
#             permission_classes=(IsAuthenticated, )
#     )
#     def logout(request):
#         access_token = request.data.get('token')
#         if not access_token:
#             return Response({'detail': 'Token is required.'}, status=status.HTTP_401_UNAUTHORIZED)
#         token = AccessToken(access_token)
#         token.blacklist()

#         return Response(status=status.HTTP_204_NO_CONTENT)
#         # refresh_token = request.data['refresh_token']
#         # token = RefreshToken(refresh_token)
#         # user = self.request.user
#         # token = get_token(user)
#         # token.blacklist()
#         # return Response(status=status.HTTP_204_NO_CONTENT)





# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout(request):
#     print(request.user)
#     print(request.headers)
#     print(request)
#     print(123)
#     access_token = request.headers.get('Authorization')
#     if not access_token:
#         return Response({'detail': 'Token is required.'}, status=status.HTTP_401_UNAUTHORIZED)
#     access_token.blacklist()
