from django.db import models
from django.conf import settings
from catalog.models import Wear

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Wear, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


# Each POSTed payload item from Checkout.tsx becomes one ShopOrder record.
class ShopOrder(models.Model):
    # optional link to user if authenticated (not required by frontend payload)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # product fields (from payload)
    external_id = models.CharField(max_length=255, blank=True, null=True)  # maps to payload.id (product id)
    wearName = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    category = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # customer & order fields
    status = models.CharField(max_length=100, default='pending')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.wearName} for {self.name} ({self.email})"



class CustomOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    measurements = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='custom-orders/', blank=True, null=True)
    status = models.CharField(max_length=30, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
