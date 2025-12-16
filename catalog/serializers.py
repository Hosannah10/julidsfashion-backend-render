from rest_framework import serializers
from .models import Wear

class WearSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Wear
        fields = ('id','wearName','price','description','category','image','created_at','updated_at')

