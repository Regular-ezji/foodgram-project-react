from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FollowViewSet, IngredientViewSet, RecipeViewSet,
                    SubscriptionsListViewSet, TagViewSet, UserViewSet,
                    get_token, logout)

router = DefaultRouter()
router.register(
    'users/subscriptions',
    SubscriptionsListViewSet,
    basename='subscriptions_list'
)
router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

router.register(
    r'users/(?P<id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', get_token, name='token'),
    path('auth/token/logout/', logout, name='logout')
]
