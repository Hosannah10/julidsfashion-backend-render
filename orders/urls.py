from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CartView, CartAddView, CartUpdateView, CartRemoveView, CartClearView,
    ShopOrderViewSet, CustomOrderViewSet
)

router = DefaultRouter()
router.register(r'shop-orders', ShopOrderViewSet, basename='shop-orders')
router.register(r'custom-orders', CustomOrderViewSet, basename='custom-orders')

urlpatterns = [
    path('cart', CartView.as_view()),
    path('cart/add', CartAddView.as_view()),
    # keep existing body-based endpoints
    path('cart/update', CartUpdateView.as_view()),
    path('cart/remove', CartRemoveView.as_view()),
    # add RESTful path-based endpoints (PUT/DELETE) for convenience and DRF compatibility
    path('cart/update/<int:id>/', CartUpdateView.as_view()),
    path('cart/remove/<int:id>/', CartRemoveView.as_view()),
    path('cart/clear', CartClearView.as_view()),
    path('', include(router.urls)),
]
