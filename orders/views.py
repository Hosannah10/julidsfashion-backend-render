from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .models import CartItem, ShopOrder, CustomOrder
from .serializers import CartItemSerializer, ShopOrderSerializer, CustomOrderSerializer
from rest_framework.decorators import action
from rest_framework import status as drf_status
from catalog.models import Wear
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user and request.user.is_authenticated else None
        user_id = request.query_params.get('userId') or request.query_params.get('user_id')
        if user is None and user_id:
            try:
                user = User.objects.get(pk=int(user_id))
            except Exception:
                return Response([], status=status.HTTP_200_OK)
        if user is None:
            return Response([], status=status.HTTP_200_OK)
        items = CartItem.objects.filter(user=user)
        serializer = CartItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

class CartAddView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Accept either Authorization header or userId in payload or query param
        user = request.user if request.user and request.user.is_authenticated else None
        user_id = request.data.get('userId') or request.data.get('user_id') or request.query_params.get('userId')
        if user is None and user_id:
            try:
                user = User.objects.get(pk=int(user_id))
            except Exception:
                return Response({'detail': 'user not found'}, status=status.HTTP_400_BAD_REQUEST)

        if user is None:
            return Response({'detail': 'Authentication required or supply userId'}, status=status.HTTP_401_UNAUTHORIZED)

        product_id = request.data.get('id') or request.data.get('product_id') or request.data.get('productId')
        if not product_id:
            return Response({'detail': 'product id required'}, status=status.HTTP_400_BAD_REQUEST)
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Wear, pk=product_id)
        obj, created = CartItem.objects.get_or_create(user=user, product=product, defaults={'quantity': quantity})
        if not created:
            obj.quantity = max(1, obj.quantity + quantity)
            obj.save()
        serializer = CartItemSerializer(obj, context={'request': request})
        return Response(serializer.data)

class CartUpdateView(APIView):
    """
    Supports:
    - POST body-based update { id: ..., quantity: ... } (legacy)
    - PUT /cart/update/<id>/ with JSON body { quantity: ... } (RESTful)
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('id')
        if not item_id:
            return Response({'detail': 'item id required'}, status=status.HTTP_400_BAD_REQUEST)
        quantity = int(request.data.get('quantity', 1))
        try:
            item = CartItem.objects.get(pk=item_id, user=request.user)
            item.quantity = max(1, quantity)
            item.save()
            return Response(CartItemSerializer(item, context={'request': request}).data)
        except CartItem.DoesNotExist:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id=None):
        # id may be provided via path param or in body
        item_id = id or request.data.get('id')
        if not item_id:
            return Response({'detail': 'item id required'}, status=status.HTTP_400_BAD_REQUEST)
        quantity = int(request.data.get('quantity', 1))
        try:
            item = CartItem.objects.get(pk=item_id, user=request.user)
            item.quantity = max(1, quantity)
            item.save()
            return Response(CartItemSerializer(item, context={'request': request}).data)
        except CartItem.DoesNotExist:
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)


class CartRemoveView(APIView):
    """
    Supports:
    - POST body-based removal { id: ... } (legacy)
    - DELETE /cart/remove/<id>/ (RESTful)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get('id')
        if not item_id:
            return Response({'detail': 'item id required'}, status=status.HTTP_400_BAD_REQUEST)
        CartItem.objects.filter(pk=item_id, user=request.user).delete()
        return Response({'detail': 'removed'})

    def delete(self, request, id=None):
        item_id = id or request.data.get('id')
        if not item_id:
            return Response({'detail': 'item id required'}, status=status.HTTP_400_BAD_REQUEST)
        CartItem.objects.filter(pk=item_id, user=request.user).delete()
        return Response({'detail': 'removed'})

class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response({'detail': 'cart cleared'})
    
class ShopOrderViewSet(viewsets.ModelViewSet):
    queryset = ShopOrder.objects.all().order_by('-created_at')
    serializer_class = ShopOrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # creation allowed only for authenticated users

    def get_queryset(self):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        if user and user.is_staff:
            return ShopOrder.objects.all().order_by('-created_at')
        if user:
            return ShopOrder.objects.filter(user=user).order_by('-created_at')
        # By requiring IsAuthenticated, this path should not run for unauthenticated users.
        return ShopOrder.objects.none()

    def create(self, request, *args, **kwargs):
        # Ensure authentication (DRF will already enforce)
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        user = request.user

        created = []

        if isinstance(data, list):
            for item in data:
                serializer = self.get_serializer(data={
                    'external_id': item.get('id'),
                    'wearName': item.get('wearName') or '',
                    'price': item.get('price') or 0,
                    'category': item.get('category') or '',
                    'description': item.get('description') or '',
                    'image': item.get('image') or '',
                    'quantity': item.get('quantity') or 1,
                    'status': item.get('status') or 'pending',
                    'total': item.get('total') or 0,
                    # store payload-supplied contact fields even though user is logged in
                    'name': item.get('name') or '',
                    'email': item.get('email') or '',
                    'phone': item.get('phone') or '',
                })
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user)
                created.append(serializer.data)
            return Response(created, status=status.HTTP_201_CREATED)

        # single object case
        item = data
        serializer = self.get_serializer(data={
            'external_id': item.get('id'),
            'wearName': item.get('wearName') or '',
            'price': item.get('price') or 0,
            'category': item.get('category') or '',
            'description': item.get('description') or '',
            'image': item.get('image') or '',
            'quantity': item.get('quantity') or 1,
            'status': item.get('status') or 'pending',
            'total': item.get('total') or 0,
            'name': item.get('name') or '',
            'email': item.get('email') or '',
            'phone': item.get('phone') or '',
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Allow delete for:
         - owner (non-staff) — they 'cancel' their own orders
         - staff (admin) — can delete any order
        """
        instance = self.get_object()  # uses get_queryset -> ensures ownership or staff
        order_id = instance.id
        self.perform_destroy(instance)
        msg = "Order deleted successfully" if request.user.is_staff else "Order cancelled successfully"
        # You can add server-side notification calls here if desired
        return Response({"detail": msg, "id": order_id}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch', 'put'], url_path='status', permission_classes=[permissions.IsAuthenticated])
    def status(self, request, pk=None):
        """
        Update only the `status` field for a ShopOrder.
        Accepts JSON body: { "status": "completed" } (or "pending")
        """
        try:
            order = self.get_object()
        except ShopOrder.DoesNotExist:
            return Response({'detail': 'Not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'Missing status'}, status=drf_status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)


class CustomOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all().order_by('-created_at')
    serializer_class = CustomOrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # REQUIRE login now
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        if user and user.is_staff:
            return CustomOrder.objects.all().order_by('-created_at')
        if user:
            return CustomOrder.objects.filter(user=user).order_by('-created_at')
        return CustomOrder.objects.none()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        order_id = instance.id
        self.perform_destroy(instance)
        msg = "Custom order deleted successfully" if request.user.is_staff else "Custom order cancelled successfully"
        return Response({"detail": msg, "id": order_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch', 'put'], url_path='status', permission_classes=[permissions.IsAuthenticated])
    def status(self, request, pk=None):
        try:
            order = self.get_object()
        except CustomOrder.DoesNotExist:
            return Response({'detail': 'Not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if not new_status:
            return Response({'detail': 'Missing status'}, status=drf_status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=drf_status.HTTP_200_OK)