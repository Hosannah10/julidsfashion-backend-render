from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

ADMIN_EMAIL = "hosannahpatrick@gmail.com"
@api_view(["POST"])
def contact_view(request):
    data = request.data

    required = ["name", "email", "phone", "message"]
    if not all(data.get(f) for f in required):
        return Response(
            {"message": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    message_body = f"""
Name: {data['name']}
Email: {data['email']}
Phone: {data['phone']}

Message:
{data['message']}
"""

    send_mail(
        subject="New Contact Message",
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ADMIN_EMAIL],
        fail_silently=False,
    )

    return Response(
        {"message": "Message sent successfully"},
        status=status.HTTP_200_OK
    )
