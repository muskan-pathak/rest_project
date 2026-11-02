from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Client, Project, ProjectAttachment, Profile
from .serializers import (UserSerializer,ClientSerializer,LoginSerializer,SendOTPSerializer,VerifyOTPSerializer,
ForgotPasswordSerializer,ResetPasswordSerializer,ProjectSerializer,ProjectAttachmentSerializer,ProfileSerializer,)
from .utils import validate_user_otp, send_limited_otp

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
                message=f'Hello {user.first_name}, your account created successfully.',
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

        send_limited_otp(user,"Your OTP Code","Your OTP is ")
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
            update_fields=['status', 'modified_by', 'modified_at']
        )

        return Response(
            {"message": "Client deactivated successfully"},
            status=status.HTTP_200_OK
        )


class ProjectListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return (
            Project.objects
            .filter(is_deleted=False)
            .exclude(project_status='Inactive')
            .prefetch_related('attachments')
            .order_by('-id')
        )

    def get(self, request):
        projects = self.get_queryset()

        paginator = PageNumberPagination()
        paginated_projects = paginator.paginate_queryset(projects, request)

        serializer = ProjectSerializer(
            paginated_projects,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = ProjectSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            project = serializer.save()

            response_serializer = ProjectSerializer(
                project,
                context={'request': request}
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return (
            Project.objects
            .filter(is_deleted=False)
            .exclude(project_status='Inactive')
            .prefetch_related('attachments')
        )

    def get_project(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_project(pk)

        if project is None:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(
            project,
            context={'request': request}
        )

        return Response(serializer.data)

    @transaction.atomic
    def put(self, request, pk):
        project = self.get_project(pk)

        if project is None:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(
            project,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            project = serializer.save()

            response_serializer = ProjectSerializer(
                project,
                context={'request': request}
            )

            return Response(response_serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @transaction.atomic
    def patch(self, request, pk):
        project = self.get_project(pk)

        if project is None:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            project = serializer.save()

            response_serializer = ProjectSerializer(
                project,
                context={'request': request}
            )

            return Response(response_serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk, attachment_id=None):

    # Individual attachment delete
        if attachment_id is not None:
            project = self.get_project(pk)

            if project is None:
                return Response(
                    {'error': 'Project not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                attachment = project.attachments.get(id=attachment_id)
            except ProjectAttachment.DoesNotExist:
                return Response(
                    {'error': 'Attachment not found in this project.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            attachment.delete()

            return Response(
                {'message': 'Attachment deleted successfully.'},
                status=status.HTTP_200_OK
            )

        # Project soft delete
        project = self.get_project(pk)

        if project is None:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        project.is_deleted = True
        project.deleted_at = timezone.now()
        project.modified_by = request.user

        project.save(
            update_fields=[
                'is_deleted',
                'deleted_at',
                'modified_by',
                'modified_at'
            ]
        )

        return Response(
            {'message': 'Project deleted successfully.'},
            status=status.HTTP_200_OK
        )
class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all().order_by('id')
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.is_default:
            return Response(
                {"message": "System profiles cannot be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.is_default:
            return Response(
                {"message": "System profiles cannot be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.is_default:
            return Response(
                {"message": "System profiles cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.delete()

        return Response(
            {"message": "Profile deleted successfully."},
            status=status.HTTP_200_OK
        )


class ProfileUsersByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, pk=profile_id)

        users = User.objects.filter(
            profile=profile,
            status='Active'
        ).order_by('id')

        return Response({
            'profile': {
                'id': profile.id,
                'name': profile.name,
            },
            'users': [
                {
                    'id': user.id,
                    'name': (
                        f"{user.first_name or ''} "
                        f"{user.last_name or ''}"
                    ).strip(),
                    'email': user.email,
                }
                for user in users
            ]
        })


class ProfileUsersByNameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, profile_name):
        profile = get_object_or_404(
            Profile,
            name__iexact=profile_name
        )

        users = User.objects.filter(
            profile=profile,
            status='Active'
        ).order_by('id')

        return Response({
            'profile': {
                'id': profile.id,
                'name': profile.name,
            },
            'users': [
                {
                    'id': user.id,
                    'name': (
                        f"{user.first_name or ''} "
                        f"{user.last_name or ''}"
                    ).strip(),
                    'email': user.email,
                }
                for user in users
            ]
        })
class InactiveRecordsAPI(APIView): # show the list of inactive users, clients and projects
    permission_classes = [AllowAny]
    def get(self, request):
        record_type = request.query_params.get('type', '').lower() # request.query_parms.get() use to access quiry parameter of url
        if record_type == 'user':
            records = User.objects.filter(status='Inactive').order_by('-id') # only inactive users
            serializer_class = UserSerializer

        elif record_type == 'client':
            records = Client.objects.filter(
                status='Inactive'
            ).order_by('-id')
            serializer_class = ClientSerializer

        elif record_type == 'project':
            records = Project.objects.filter(
                is_deleted=True
            ).prefetch_related('attachments').order_by('-id') # fetch objects efficiently
            serializer_class = ProjectSerializer

        else:
            return Response(
                {"error": "Invalid type. Please use user, client, or project."},
                status=status.HTTP_400_BAD_REQUEST
            )

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(records, request)

        if record_type == 'project':
            serializer = serializer_class(page,many=True,context={'request': request})
        else:
            serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class RestoreRecordAPI(APIView): # inactive records ko restore krne ke liye
    permission_classes = [AllowAny]

    def patch(self, request,record_type,pk):
        record_type = record_type.lower()
        if record_type == 'user':
            record = User.objects.filter(pk=pk,status='Inactive').first() # check krta h ki user inactive h ya nhi
            serializer_class = UserSerializer                       # first() use for getting first record if no record then none return

        elif record_type == 'client':
            record = Client.objects.filter(pk=pk,status='Inactive').first()
            serializer_class = ClientSerializer

        elif record_type == 'project':
            record = Project.objects.filter(pk=pk,is_deleted=True).prefetch_related('attachments').first() # related attachments ko efficiently retrieve kr leta h
            serializer_class = ProjectSerializer

        else:
            return Response(
                {"error": "Invalid type. Use user, client, or project"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if record is None:
            return Response(
                {"error": "Inactive record not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        # Restore the selected record
        if record_type in ['user', 'client']:
            record.status = 'Active' # status update kr rhe h

            if record_type == 'client':
                record.modified_by = request.user
                record.save(update_fields=['status', 'modified_by', 'modified_at'])
            else:
                record.save(update_fields=['status']) # for user

        else:
            record.is_deleted = False
            record.deleted_at = None
            record.modified_by = request.user
            record.save(update_fields=['is_deleted','deleted_at','modified_by','modified_at'])
    
        if record_type == 'project':
            serializer = serializer_class(
                record,
                context={'request': request}
            )
        else:
            serializer = serializer_class(record) # agr user ya client restore hua h then serializer ko record pass kr rhe h

        return Response(
            {
                "message": "Record restored successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )















