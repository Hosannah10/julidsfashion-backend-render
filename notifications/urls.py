from django.urls import path
from . import views

urlpatterns = [
    path('notifications/shop-order-placed/', views.shop_order_placed),
    path('notifications/shop-order-completed/', views.shop_order_completed),
    path('notifications/custom-order-placed/', views.custom_order_placed),
    path('notifications/custom-order-completed/', views.custom_order_completed),
]
