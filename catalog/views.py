from rest_framework import viewsets, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import Wear
from .serializers import WearSerializer
from rest_framework.response import Response

class WearViewSet(viewsets.ModelViewSet):
    queryset = Wear.objects.all().order_by('-created_at')
    serializer_class = WearSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # allow multipart/form-data for image upload

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        order_id = instance.id
        self.perform_destroy(instance)
        msg = "Wear deleted successfully"
        return Response({"detail": msg, "id": order_id})
