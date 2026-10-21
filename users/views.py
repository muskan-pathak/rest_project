from django.core import paginator
from django.db.migrations import serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import request, status

import users
from .models import User,Client
from .serializers import UserSerializer,ClientSerializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.conf import settings
from rest_framework.pagination import PageNumberPagination





class UserListCreateAPI(APIView):   
    permission_classes = [AllowAny]  
    def get(self, request):  
        users = User.objects.filter(status='Active') 
        paginator = PageNumberPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    
    def post(self, request):
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
        user = self.get_user(pk)  

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

    def patch(self, request, pk):  
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

        user.status = 'Inactive' 
        user.save(update_fields=['status'])

        return Response(
            {"message": "User deactivated successfully"},
            status=status.HTTP_200_OK
        )


class ClientListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request): 
        clients = Client.objects.filter(status='Active') 
        paginator = PageNumberPagination()
        paginated_clients = paginator.paginate_queryset(clients, request)
        serializer = ClientSerializer(paginated_clients, many=True)
        return paginator.get_paginated_response(serializer.data)
        # serializer = ClientSerializer(clients, many=True)

        # return Response(serializer.data, status=status.HTTP_200_OK)

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
        client = self.get_client(pk)

        if client is None:
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

   
    def patch(self, request, pk):
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







