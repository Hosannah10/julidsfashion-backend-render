from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Accept "name" or "firstName" (frontend may use name)
        name = request.data.get('name') or request.data.get('firstName') or ''
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        username = email.split('@')[0]
        user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': {'id': user.id, 'name': user.first_name, 'email': user.email}
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        # django authenticate uses username field by default - since we use email as USERNAME_FIELD, this works
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': {'id': user.id, 'name': user.first_name, 'email': user.email, 'is_staff': user.is_staff,}
        }, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        frontend_url = request.data.get('frontend_url') or request.data.get('frontendUrl') or 'http://localhost:3000'
        if not email:
            return Response({'detail': 'email required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal existence
            return Response({'detail': 'If an account exists, a reset link was sent'}, status=status.HTTP_200_OK)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = f"{frontend_url.rstrip('/')}/reset-password/{uid}-{token}"
        # console email backend will print this
        send_mail('Password reset', f'Use this link to reset your password: {reset_link}', None, [user.email])
        return Response({'detail': 'If an account exists, a reset link was sent'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_combined = request.data.get('token')
        password = request.data.get('password')
        if not token_combined or not password:
            return Response({'detail': 'token and password required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uidb64, token = token_combined.split('-', 1)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'detail': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        if not token_generator.check_token(user, token):
            return Response({'detail': 'invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({'detail': 'password reset successful'}, status=status.HTTP_200_OK)
