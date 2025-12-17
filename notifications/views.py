from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.mail import send_mail
from django.conf import settings


ADMIN_EMAIL = "hosannahpatrick@gmail.com"
DEV_EMAIL = "zanarick100@gmail.com"


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def shop_order_placed(request):
    email = request.data.get('email')
    order_id = request.data.get('order_id') or request.data.get('id')

    subject = request.data.get('subject') or f"Order {order_id} placed"
    body = request.data.get('body') or f"Your order {order_id} was placed successfully."

    subject_admin = f"Shop Order {order_id} placed"
    body_admin = (
        f"Shop Order {order_id} has just been placed by customer ({email}). "
        "Open the admin page for details."
    )

    if email:
        # Email to the customer
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

        # Email to admin
        send_mail(subject_admin, body_admin, settings.DEFAULT_FROM_EMAIL, [ADMIN_EMAIL])

    return Response({"detail": "notification sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def shop_order_completed(request):
    email = request.data.get('email')
    order_id = request.data.get('order_id') or request.data.get('id')

    subject = request.data.get('subject') or f"Order {order_id} completed"
    body = request.data.get(
        'body',
        f"Your order {order_id} is complete. Thank you for patronizing Julids Fashion."
    )

    if email:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

    return Response({"detail": "notification sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def custom_order_placed(request):
    email = request.data.get('email')

    subject = request.data.get('subject') or "Custom order received"
    body = request.data.get('body') or "We received your custom order."

    subject_admin = "Custom Order placed"
    body_admin = (
        f"A custom order has just been placed by customer ({email}). "
        "Open the admin page for more details."
    )

    if email:
        # customer
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

        # admin
        send_mail(subject_admin, body_admin, settings.DEFAULT_FROM_EMAIL, [ADMIN_EMAIL])

    return Response({"detail": "notification sent"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def custom_order_completed(request):
    email = request.data.get('email')

    subject = request.data.get('subject') or "Custom order update"
    body = request.data.get(
        'body',
        "Your custom order is complete. Thank you for patronizing Julids Fashion."
    )

    if email:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email])

    return Response({"detail": "notification sent"}, status=status.HTTP_200_OK)
