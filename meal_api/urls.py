# from rest_framework import routers
from rest_framework_nested import routers

from .views import (
    MenuViewSet,
    MenuOptionViewSet,
    OrderViewSet,
)

router = routers.SimpleRouter()
router.register('menus', MenuViewSet, basename='menu')
router.register('orders', OrderViewSet, basename='order')

menus_router = routers.NestedSimpleRouter(
    router,
    r'menus',
    lookup='menu',
)
menus_router.register('options', MenuOptionViewSet, basename='menu-option')


app_name = 'meal_api'

urlpatterns = router.urls + menus_router.urls
