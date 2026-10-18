from datetime import timedelta # calculate otp expiry time
import secrets # generate otp
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)

User = get_user_model()


def generate_and_send_otp(user, subject, message_prefix): # generate otp save it on user and email it
    otp = f"{secrets.randbelow(900000) + 100000}"
    now = timezone.now()

    user.otp_hash = make_password(otp)
    user.otp_created_at = now # saves the time when otp created
    user.otp_expires_at = now + timedelta(minutes=5) # otp expire time
    user.otp_is_used = False
    user.save(update_fields=[
        "otp_hash",
        "otp_created_at",
        "otp_expires_at",
        "otp_is_used",
    ])

    send_mail(
        subject=subject,
        message=f"{message_prefix}{otp}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def validate_user_otp(user, otp):    # check otp and validate it
    if (
        not user.otp_hash
        or not user.otp_expires_at # if expiry time is not save it cannot validate safely
        or user.otp_is_used
        or user.otp_expires_at <= timezone.now()
    ):
        return False

    return check_password(otp, user.otp_hash) # compare otp


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST, # if validation fails
            )

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email, status="Active")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(
            request,
            username=user.username,
            password=password,
        )

        if user is None:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class SendOTPAPIView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email, status="Active")
        except User.DoesNotExist:
            return Response(
                {"error": "No active user found with this email"},
                status=status.HTTP_404_NOT_FOUND,
            )

        generate_and_send_otp(
            user,
            "Your OTP Code",
            "Your OTP is ",
        )

        return Response(
            {"message": "OTP sent successfully to your email"},
            status=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email, status="Active")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not validate_user_otp(user, otp):
            return Response(
                {"error": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.otp_is_used = True # mark otp use
        user.save(update_fields=["otp_is_used"]) # save it so taht cannot used again

        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email, status="Active")
        except User.DoesNotExist:
            return Response(
                {"error": "No active user found with this email"},
                status=status.HTTP_404_NOT_FOUND,
            )

        generate_and_send_otp(
            user,
            "Password Reset OTP",
            "Your password reset OTP is ",
        )

        return Response(
            {"message": "Password reset OTP sent successfully"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email, status="Active")
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not validate_user_otp(user, otp):
            return Response(
                {"error": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.otp_is_used = True
        user.save(update_fields=["password", "otp_is_used"])

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )




















