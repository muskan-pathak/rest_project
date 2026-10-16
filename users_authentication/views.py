from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone

from datetime import timedelta
import secrets # otp generate krne ke liye 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmailOTP
from .serializers import LoginSerializer, SendOTPSerializer, VerifyOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer
from django.contrib.auth.hashers import check_password

User = get_user_model()

class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(
                    email=email,
                    status='Active'
                )
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user = authenticate(
                request,
                username=user.username,
                password=password
            )

            if user is None:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'message': 'Login successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class SendOTPAPIView(APIView):

    def post(self, request):
        data=request.data
        print(">>>>>>>>>>>>>",data)
        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        print(">>>>>>>>>>>>>",email)

        try:
            user = User.objects.get(
                email=email,
                status='Active'
            )
            print(">>>>>>>>>>>>>",user)
        except User.DoesNotExist:
            return Response(
                {'error': 'No active user found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = f"{secrets.randbelow(900000) + 100000}"

        now = timezone.now()

        EmailOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        EmailOTP.objects.create(
            user=user,
            otp_hash=make_password(otp),
            expires_at=now + timedelta(minutes=5)
        )

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {otp}. It expires in 5 minutes.',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {'message': 'OTP sent successfully to your email'},
            status=status.HTTP_200_OK
        )


class VerifyOTPAPIView(APIView):

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(
                email=email,
                status='Active'
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record = EmailOTP.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if otp_record is None or not check_password(
            otp,
            otp_record.otp_hash
        ):
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record.is_used = True
        otp_record.save(update_fields=['is_used'])

        return Response(
            {'message': 'OTP verified successfully'},
            status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(
                email=email,
                status='Active'
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'No active user found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = f"{secrets.randbelow(900000) + 100000}"
        now = timezone.now()

        EmailOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        EmailOTP.objects.create(
            user=user,
            otp_hash=make_password(otp),
            expires_at=now + timedelta(minutes=5)
        )

        send_mail(
            subject='Password Reset OTP',
            message=f'Your password reset OTP is {otp}. It expires in 5 minutes.',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response(
            {'message': 'Password reset OTP sent successfully'},
            status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(
                email=email,
                status='Active'
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'No active user found with this email'},
                status=status.HTTP_404_NOT_FOUND
            )

        otp = f"{secrets.randbelow(900000) + 100000}"
        now = timezone.now()

        EmailOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        EmailOTP.objects.create(
            user=user,
            otp_hash=make_password(otp),
            expires_at=now + timedelta(minutes=5)
        )

        send_mail(
            subject='Password Reset OTP',
            message=f'Your password reset OTP is {otp}. It expires in 5 minutes.',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response(
            {'message': 'Password reset OTP sent successfully'},
            status=status.HTTP_200_OK
        )


class ResetPasswordAPIView(APIView):

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email, status='Active')
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record = EmailOTP.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if otp_record is None or not check_password(
            otp, otp_record.otp_hash
        ):
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])

        otp_record.is_used = True
        otp_record.save(update_fields=['is_used'])

        return Response(
            {'message': 'Password reset successfully'},
            status=status.HTTP_200_OK
        )



















