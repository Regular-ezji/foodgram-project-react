from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    SubscriptionsListViewSet, TagViewSet, UserViewSet,
                    get_token)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', get_token, name='token'),
    # path(
    #     'recipes/<int:user_id>/subscribe/',
    #     FollowCreateDestroyViewSet.as_view()
    # )
    # path('auth/token/logout/', logout, name='logout'),
    # path('users/'),
    # path(
    #     'users/subscriptions/',
    #     SubscriptionsListViewSet.as_view(),
    # ),
    # path(
    #     'users/<int:user_id>/subscribe/',
    #     FollowCreateDestroyViewSet.as_view()
    # )
]
