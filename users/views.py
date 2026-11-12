from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, request, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Client, Project, ProjectAttachment, Profile,ProjectTask,TaskComment
from .serializers import (UserSerializer,ClientSerializer,LoginSerializer,SendOTPSerializer,VerifyOTPSerializer,
ForgotPasswordSerializer,ResetPasswordSerializer,ProjectSerializer,ProjectAttachmentSerializer,ProfileSerializer,ProjectTaskSerializer,TaskCommentSerializer)
from .utils import validate_user_otp, send_limited_otp
import logging
# class Pagination(PageNumberPagination):
#     page_size = 5
#     page_size_query_param = 'page_size'
#     max_page_size = 100

class UserListCreateAPI(APIView): # this is for creating users and listing all users
    permission_classes = [IsAuthenticated] # this for allowing any user to acess this view
    def get(self, request):
        # users = User.objects.filter(status='Active')
        user_status = request.query_params.get('status', 'Active')
        users = User.objects.filter(status__iexact=user_status)

        # General search
        search = request.query_params.get("search", "").strip() # query_parms url ki query parameter ko access krta h

        if search:
            for word in search.split():
                users = users.filter( # q object ko use krke multiple fields me search kr skte h
                    Q(username__icontains=word) |   # contains partial match krta h, icontains case insensitive match krta h
                    Q(email__icontains=word) |
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(phone__icontains=word) |
                    Q(profile__name__icontains=word)
                )

    # Individual filters
        first_name = request.query_params.get("first_name", "").strip()
        last_name = request.query_params.get("last_name", "").strip()
        email = request.query_params.get("email", "").strip()
        profile = request.query_params.get("profile", "").strip()
        phone = request.query_params.get("phone", "").strip()

        if first_name:
            users = users.filter(first_name__icontains=first_name)

        if last_name:
            users = users.filter(last_name__icontains=last_name)

        if email:
            users = users.filter(email__icontains=email)

        if profile:
            users = users.filter(profile__name__iexact=profile)

        if phone:
            users = users.filter(phone__icontains=phone)

        # Pagination
        paginator = PageNumberPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        serializer = UserSerializer(paginated_users, many=True)

        return paginator.get_paginated_response(serializer.data)
    

    # def post(self, request): # this for creating new user and send welcome email after craetion
    #     serializer = UserSerializer(data=request.data)

    #     if serializer.is_valid():
    #         user = serializer.save()
    #         try:
    #             send_mail(
    #             subject='Welcome to Our Platform',
    #             message=f'Hello {user.first_name}, your account created successfully.',
    #             from_email=settings.DEFAULT_FROM_EMAIL,  
    #             recipient_list=[user.email],
    #             fail_silently=False,
    #             )
             
    #         except Exception as e:
    #             print(f"Failed to send email >>>>>>> : {str(e)}")
    #             return Response(
    #                 {"error": f"User created but failed to send email: {str(e)}"},
    #                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #             )

    #         return Response(
    #             UserSerializer(user).data,
    #             status=status.HTTP_201_CREATED 
    #         )

    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST 
    #     )  
    def post(self, request):

        # Only Admin and Super Admin can create users
        if request.user.profile is None or request.user.profile.name.strip().casefold() not in ["admin", "super admin"]:
            return Response(
                {"error": "Only Admin or Super Admin can create users."},
                status=status.HTTP_403_FORBIDDEN
            )

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
        client_status = request.query_params.get('status', 'Active')
        clients = Client.objects.filter(status__iexact=client_status) 
         # General Search
        search = request.query_params.get("search", "").strip()

        if search:
            for word in search.split():
                clients = clients.filter(
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(email__icontains=word) |
                    Q(contact_number__icontains=word) |
                    Q(country__icontains=word) |
                    Q(address__icontains=word)
                )

        # Individual Filters
        first_name = request.query_params.get("first_name", "").strip()
        last_name = request.query_params.get("last_name", "").strip()
        email = request.query_params.get("email", "").strip()
        contact_number = request.query_params.get("contact_number", "").strip()
        country = request.query_params.get("country", "").strip()
        address = request.query_params.get("address", "").strip()

        if first_name:
            clients = clients.filter(first_name__icontains=first_name)

        if last_name:
            clients = clients.filter(last_name__icontains=last_name)

        if email:
            clients = clients.filter(email__icontains=email)

        if contact_number:
            clients = clients.filter(contact_number__exact=contact_number)

        if country:
            clients = clients.filter(country__iexact=country)

        if address:
            clients = clients.filter(address__icontains=address)

        # Pagination
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

def send_project_notification(project):
    client = project.client

    if not client or not client.email:
        return False

    manager = project.manager

    if manager:
        manager_name = (
            f"{manager.first_name} {manager.last_name}"
        ).strip()

        manager_name = manager_name or manager.email or "Not available"
        manager_email = manager.email or "Not available"
    else:
        manager_name = "Not assigned"
        manager_email = "Not assigned"

    subject = f"New Project Assigned: {project.project_title}"

    message = f"""
Hello {client.first_name + ' ' + client.last_name if client.first_name and client.last_name else 'Client'},

A new project has been created as per your requirements.

Project Details:

Project Title: {project.project_title}
Project Status: {project.project_status}
Description: {project.description or 'Not provided'}

Assigned Manager:
Name: {manager_name}
Email: {manager_email}

Regards,
Project Management Team
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            fail_silently=False
        )
        return True

    except Exception:
        logging.getLogger(__name__).exception(
            "Project notification email could not be sent."
        )
        return False

def send_manager_notification(project):
    manager = project.manager

    if not manager or not manager.email:
        return False

    client = project.client

    if client:
        client_name = (
            f"{client.first_name} {client.last_name}"
        ).strip()

        client_name = client_name or "Not available"
        client_email = client.email or "Not available"
    else:
        client_name = "Not assigned"
        client_email = "Not available"

    subject = f"New Project Assigned: {project.project_title}"

    message = f"""
Hello {manager.first_name or 'Manager'},

A new project has been assigned to you.

Project Details:

Project Title: {project.project_title}
Project Status: {project.project_status}
Description: {project.description or 'Not provided'}

Associated Client:
Name: {client_name}
Email: {client_email}

Regards,
Project Management Team
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[manager.email],
            fail_silently=False
        )
        return True

    except Exception:
        logging.getLogger(__name__).exception(
            "Manager notification email could not be sent."
        )
        return False


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
        # projects = self.get_queryset()
        project_status_filter = request.query_params.get('status', 'Active')

        if project_status_filter.lower() == 'inactive':
            projects = Project.objects.filter(
                is_deleted=True
            ).prefetch_related('attachments').order_by('-id')
        else:
            projects = self.get_queryset()

        search = request.query_params.get("search", "").strip()

        if search:
            for word in search.split():
                projects = projects.filter(
                    Q(project_title__icontains=word) |
                    Q(project_type__icontains=word) |
                    Q(description__icontains=word) |
                    Q(client__first_name__icontains=word) |
                    Q(client__last_name__icontains=word) |
                    Q(client__email__icontains=word) |
                    Q(manager__first_name__icontains=word) |
                    Q(manager__last_name__icontains=word) |
                    Q(manager__email__icontains=word)
                )

        # Individual filters
        project_title = request.query_params.get("project_title", "").strip()
        project_type = request.query_params.get("project_type", "").strip()
        description = request.query_params.get("description", "").strip()
        project_status = request.query_params.get("project_status", "").strip()
        client = request.query_params.get("client", "").strip()
        manager = request.query_params.get("manager", "").strip()

        if project_title:
            projects = projects.filter(project_title__icontains=project_title)

        if project_type:
            projects = projects.filter(project_type__icontains=project_type)

        if description:
            projects = projects.filter(description__icontains=description)

        if project_status:
            projects = projects.filter(project_status__iexact=project_status)

        if client.isdigit():
            projects = projects.filter(client_id=int(client))

        client_first_name = request.query_params.get("client_first_name")
        client_last_name = request.query_params.get("client_last_name")
        client_username = request.query_params.get("client_username")
        client_email = request.query_params.get("client_email")


        if client_first_name:
            projects = projects.filter(client__first_name__icontains=client_first_name)


        if client_last_name:
            projects = projects.filter(client__last_name__icontains=client_last_name)


        if client_username:
            projects = projects.filter(client__username__icontains=client_username)


        if client_email:
            projects = projects.filter(client__email__icontains=client_email)
        # elif client:
        #     for word in client.split():
        #         projects = projects.filter(
        #             Q(client__first_name__icontains=word) |
        #             Q(client__last_name__icontains=word) |
        #             Q(client__email__icontains=word)
        #         )

        if manager.isdigit():
            projects = projects.filter(manager_id=int(manager))

        manager_first_name = request.query_params.get("manager_first_name")
        manager_last_name = request.query_params.get("manager_last_name")
        manager_username = request.query_params.get("manager_username")
        manager_email = request.query_params.get("manager_email")


        if manager_first_name:
            projects = projects.filter(manager__first_name__icontains=manager_first_name)


        if manager_last_name:
            projects = projects.filter(manager__last_name__icontains=manager_last_name)


        if manager_username:
            projects = projects.filter(manager__username__icontains=manager_username)


        if manager_email:
            projects = projects.filter(manager__email__icontains=manager_email)
        # elif manager:
        #     for word in manager.split():
        #         projects = projects.filter(
        #             Q(manager__first_name__icontains=word) |
        #             Q(manager__last_name__icontains=word) |
        #             Q(manager__username__icontains=word) |
        #             Q(manager__email__icontains=word)
        #         )

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

            transaction.on_commit(
                lambda: send_project_notification(project)
            )

            transaction.on_commit(
                lambda: send_manager_notification(project)
            )

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

    # @transaction.atomic
    # def post(self, request):
    #     serializer = ProjectSerializer(
    #         data=request.data,
    #         context={'request': request}
    #     )

    #     if serializer.is_valid():
    #         project = serializer.save()

    #         response_serializer = ProjectSerializer(
    #             project,
    #             context={'request': request}
    #         )

    #         return Response(
    #             response_serializer.data,
    #             status=status.HTTP_201_CREATED
    #         )

    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST
    #     )


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
                {"message": "This is default profile. It cannot be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.is_default:
            return Response(
                {"message": "This is default profile. It cannot be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.is_default:
            return Response(
                {"message": "This is default profile. it can not be updated."},
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

class RestoreUserAPI(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, ids=None):

        # Get IDs from URL or request body
        if ids is not None:
            ids = ids.split(',')
        else:
            ids = request.data.get('ids', [])

        # Validate IDs
        if not isinstance(ids, list):
            return Response(
                {"error": "Please provide IDs as a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not ids:
            return Response(
                {"error": "Please provide at least one user ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ids = list(dict.fromkeys(int(user_id) for user_id in ids))
        except (ValueError, TypeError):
            return Response(
                {"error": "All IDs must be valid integers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find inactive users
        inactive_users = User.objects.filter(id__in=ids,status='Inactive' )
        restored_ids = list(inactive_users.values_list('id', flat=True) )
     
        # Restore inactive users
        inactive_users.update(status='Active')

        # Find already active users
        active_ids = list(User.objects.filter(id__in=ids,status='Active').values_list('id', flat=True))
        skipped_ids = [user_id for user_id in ids
            if user_id in active_ids and user_id not in restored_ids
        ]
        # Find IDs that do not exist
        existing_ids = set(
            User.objects.filter(id__in=ids)
            .values_list('id', flat=True)
        )

        not_found_ids = [user_id for user_id in ids
            if user_id not in existing_ids
        ]

        # Prepare response message
        if restored_ids:
            message = (
                f"{len(restored_ids)} user(s) restored successfully."
            )
        elif skipped_ids and not not_found_ids:
            message = "All provided users are already active."
        else:
            message = "No inactive users found to restore."

        response_data = {
            "message": message,
            "restored_ids": restored_ids,
            "skipped_ids": skipped_ids
        }
        if not_found_ids:
            response_data["not_found_ids"] = not_found_ids

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
    
class RestoreClientAPI(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, ids=None):

        # Get IDs from URL or request body
        if ids is not None:
            ids = ids.split(',')
        else:
            ids = request.data.get('ids', [])

        # Validate IDs
        if not isinstance(ids, list):
            return Response(
                {"error": "Please provide IDs as a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not ids:
            return Response(
                {"error": "Please provide at least one client ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ids = list(dict.fromkeys(int(client_id) for client_id in ids))
        except (ValueError, TypeError):
            return Response(
                {"error": "All IDs must be valid integers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find inactive clients
        inactive_clients = Client.objects.filter(
            id__in=ids,
            status='Inactive'
        )

        restored_ids = list(
            inactive_clients.values_list('id', flat=True)
        )

        # Restore inactive clients
        inactive_clients.update(status='Active')

        # Find already active clients
        active_ids = list(
            Client.objects.filter(
                id__in=ids,
                status='Active'
            ).values_list('id', flat=True)
        )

        skipped_ids = [
            client_id for client_id in ids
            if client_id in active_ids and client_id not in restored_ids
        ]

        # Find IDs that do not exist
        existing_ids = set(
            Client.objects.filter(id__in=ids)
            .values_list('id', flat=True)
        )

        not_found_ids = [
            client_id for client_id in ids
            if client_id not in existing_ids
        ]

        # Prepare response message
        if restored_ids:
            message = f"{len(restored_ids)} client(s) restored successfully."
        elif skipped_ids and not not_found_ids:
            message = "All provided clients are already active."
        else:
            message = "No inactive clients found to restore."

        response_data = {
            "message": message,
            "restored_ids": restored_ids,
            "skipped_ids": skipped_ids
        }

        if not_found_ids:
            response_data["not_found_ids"] = not_found_ids

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

class RestoreProjectAPI(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, ids=None):

        # Get IDs from URL or request body
        if ids is not None:
            ids = ids.split(',')
        else:
            ids = request.data.get('ids', [])

        # Validate IDs
        if not isinstance(ids, list):
            return Response(
                {"error": "Please provide IDs as a list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not ids:
            return Response(
                {"error": "Please provide at least one project ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ids = list(dict.fromkeys(int(project_id) for project_id in ids))
        except (ValueError, TypeError):
            return Response(
                {"error": "All IDs must be valid integers."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find deleted projects
        deleted_projects = Project.objects.filter(
            id__in=ids,
            is_deleted=True
        )

        restored_ids = list(
            deleted_projects.values_list('id', flat=True)
        )

        # Restore deleted projects
        deleted_projects.update(
            is_deleted=False,
            deleted_at=None
        )

        # Change project_status from Inactive to Active
        Project.objects.filter(
            id__in=restored_ids,
            project_status__iexact='Inactive'
        ).update(project_status='Active')

        # Find projects that are already active
        active_ids = list(
            Project.objects.filter(
                id__in=ids,
                is_deleted=False
            ).values_list('id', flat=True)
        )

        skipped_ids = [
            project_id for project_id in ids
            if project_id in active_ids and project_id not in restored_ids
        ]

        # Find IDs that do not exist
        existing_ids = set(
            Project.objects.filter(id__in=ids)
            .values_list('id', flat=True)
        )

        not_found_ids = [
            project_id for project_id in ids
            if project_id not in existing_ids
        ]

        # Prepare response message
        if restored_ids:
            message = f"{len(restored_ids)} project(s) restored successfully."
        elif skipped_ids and not not_found_ids:
            message = "All provided projects are already active."
        else:
            message = "No deleted projects found to restore."

        response_data = {
            "message": message,
            "restored_ids": restored_ids,
            "skipped_ids": skipped_ids
        }

        if not_found_ids:
            response_data["not_found_ids"] = not_found_ids

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

class ProjectTaskListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ProjectTask.objects
            .filter(is_deleted=False)
            .select_related(
                'project',
                'assign_by',
                'assign_to',
                'assign_by__profile',
                'assign_to__profile'
            )
            .order_by('-id')
        )

    # GET - List all active tasks
    def get(self, request):

        tasks = self.get_queryset()

        paginator = PageNumberPagination()
        paginated_tasks = paginator.paginate_queryset(
            tasks,
            request
        )

        serializer = ProjectTaskSerializer(
            paginated_tasks,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    # POST - Create new task
    def post(self, request):

        serializer = ProjectTaskSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            task = serializer.save(
                created_by=request.user,
                updated_by=request.user
            )

            response_serializer = ProjectTaskSerializer(
                task,
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

class ProjectTaskDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_task(self, pk):
        try:
            return (
                ProjectTask.objects
                .filter(is_deleted=False)
                .select_related(
                    'project',
                    'assign_by',
                    'assign_to',
                    'assign_by__profile',
                    'assign_to__profile'
                )
                .get(pk=pk)
            )

        except ProjectTask.DoesNotExist:
            return None

    # GET - Retrieve single task
    def get(self, request, pk):

        task = self.get_task(pk)

        if task is None:
            return Response(
                {'error': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectTaskSerializer(
            task,
            context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # PUT - Complete update
    def put(self, request, pk):

        task = self.get_task(pk)

        if task is None:
            return Response(
                {'error': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectTaskSerializer(
            task,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            task = serializer.save(
                updated_by=request.user
            )

            response_serializer = ProjectTaskSerializer(
                task,
                context={'request': request}
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # PATCH - Partial update
    def patch(self, request, pk):

        task = self.get_task(pk)

        if task is None:
            return Response(
                {'error': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProjectTaskSerializer(
            task,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():

            task = serializer.save(
                updated_by=request.user
            )

            response_serializer = ProjectTaskSerializer(
                task,
                context={'request': request}
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE - Soft delete
    def delete(self, request, pk):

        task = self.get_task(pk)

        if task is None:
            return Response(
                {'error': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        task.is_deleted = True
        task.updated_by = request.user

        task.save(
            update_fields=[
                'is_deleted',
                'updated_by',
                'updated_at'
            ]
        )

        return Response(
            {'message': 'Task deleted successfully.'},
            status=status.HTTP_200_OK
        )



class TaskCommentListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            TaskComment.objects
            .filter(task__is_deleted=False)
            .select_related('task', 'user')
            .order_by('-id')
        )

    # GET - List all task comments
    def get(self, request):

        comments = self.get_queryset()

        task_id = request.query_params.get('task_id')

        if task_id:
            comments = comments.filter(task_id=task_id)

        paginator = PageNumberPagination()
        paginated_comments = paginator.paginate_queryset(
            comments,
            request
        )

        serializer = TaskCommentSerializer(
            paginated_comments,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    # POST - Create new task comment
    def post(self, request):

        serializer = TaskCommentSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            comment = serializer.save(
                user=request.user
            )

            response_serializer = TaskCommentSerializer(
                comment,
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

class TaskCommentDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            TaskComment.objects.select_related('task', 'user'),
            pk=pk,task__is_deleted=False)
        
    def get(self, request, pk):     # for single task details
        comment = self.get_object(pk)

        serializer = TaskCommentSerializer(
            comment,context={'request': request})

        return Response(
            serializer.data,status=status.HTTP_200_OK)   

    def put(self, request, pk):
        comment = self.get_object(pk)

        serializer = TaskCommentSerializer(comment,data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def patch(self, request, pk):
        comment = self.get_object(pk)

        serializer = TaskCommentSerializer(comment,data=request.data,partial=True,
            context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):  # hard delete comment
        comment = self.get_object(pk)
        comment.delete()

        return Response(
            {"message": "Task comment deleted successfully."},
            status=status.HTTP_200_OK
        )


















