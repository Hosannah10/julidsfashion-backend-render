from rest_framework import serializers
from .models import CartItem, ShopOrder, CustomOrder
from catalog.serializers import WearSerializer
from catalog.models import Wear

class CartItemSerializer(serializers.ModelSerializer):
    product = WearSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, source='product', queryset=Wear.objects.all())

    class Meta:
        model = CartItem
        fields = ('id','user','product','product_id','quantity','created_at')
        read_only_fields = ('user','created_at')

class ShopOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopOrder
        fields = ('id','external_id','wearName','price','category','description','image','quantity','status','total','name','email','phone','user','created_at')
        read_only_fields = ('id','created_at','user')


class CustomOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOrder
        fields = '__all__'
        read_only_fields = ('created_at',)


