from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from .models import User,Client
from .serializers import UserSerializer,ClientSerializer, LoginSerializer,SendOTPSerializer, VerifyOTPSerializer,ForgotPasswordSerializer,ResetPasswordSerializer 
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_and_send_otp, validate_user_otp
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from .utils import send_limited_otp

class UserListCreateAPI(APIView): # this is for creating users and listing all users
    permission_classes = [AllowAny]  # this for allowing any user to acess this view
    def get(self, request):  # list all active users
        users = User.objects.filter(status='Active') # ensuring only active users
        paginator = PageNumberPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    def post(self, request): # this for creating new user and send welcome email after craetion
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            try:
                send_mail(
                subject='Welcome to Our Platform',
                message=f'Hello {user.first_name}, your account has been created successfully.',
                from_email=settings.DEFAULT_FROM_EMAIL,  
                recipient_list=[user.email],
                fail_silently=False,
                )
             
            except Exception as e:
                print(f"Failed to send email >>>>>>> : {str(e)}")
                return Response(
                    {"error": f"User created but failed to send email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED 
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST 
        )  
class UserDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk, status='Active')
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_user(pk)  # find active user by primary key by calling helper method

        if user is None:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk): 
        user = self.get_user(pk)

        if user is None:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):  # update partial data 
        user = self.get_user(pk)

        if user is None:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user = self.get_user(pk)

        if user is None:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.status = 'Inactive' # mark user as inactive not deete it
        user.save(update_fields=['status'])

        return Response(
            {"message": "User deactivated successfully"},
            status=status.HTTP_200_OK
        )

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST, 
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
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(
                email=email,
                status="Active"
            )
        except User.DoesNotExist:
            return Response(
                {"error": "No active user found with this email"},
                status=status.HTTP_404_NOT_FOUND
            )

        send_limited_otp(
            user,
            "Your OTP Code",
            "Your OTP is "
        )

        return Response(
            {"message": "OTP sent successfully to your email"},
            status=status.HTTP_200_OK
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

        user.otp_is_used = True 
        user.save(update_fields=["otp_is_used"]) 

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
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(
                email=email,
                status="Active"
            )
        except User.DoesNotExist:
            return Response(
                {"error": "No active user found with this email"},
                status=status.HTTP_404_NOT_FOUND
            )

        send_limited_otp(
            user,
            "Password Reset OTP",
            "Your password reset OTP is "
        )

        return Response(
            {"message": "Password reset OTP sent successfully"},
            status=status.HTTP_200_OK
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


class ClientListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request): # to get the list of clients
        clients = Client.objects.filter(status='Active') # only active satus clients
        paginator = PageNumberPagination()
        paginated_clients = paginator.paginate_queryset(clients, request)
        serializer = ClientSerializer(paginated_clients, many=True)
        return paginator.get_paginated_response(serializer.data)
       

    def post(self, request): 
        serializer = ClientSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                modified_by=request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class ClientDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_client(self, pk):
        try:
            return Client.objects.get(pk=pk, status='Active')
        except Client.DoesNotExist:
            return None

    def get(self, request, pk):
        client = self.get_client(pk) # calling helper method to get active client

        if client is None: # check krta h helper method ko clent mila ya nhi
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def put(self, request, pk):
        client = self.get_client(pk)

        if client is None:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientSerializer(client, data=request.data)

        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

   
    def patch(self, request, pk): # update partial data of client
        client = self.get_client(pk)

        if client is None:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientSerializer(
            client,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    
    def delete(self, request, pk):
        client = self.get_client(pk)

        if client is None:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        client.status = 'Inactive'
        client.modified_by = request.user
        client.save(
            update_fields=['status', 'modified_at', 'modified_by']
        )

        return Response(
            {"message": "Client deactivated successfully"},
            status=status.HTTP_200_OK
        )










