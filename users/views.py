from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


class UserListCreateAPI(APIView):   # this is for crating users and listing all users
    permission_classes = [IsAuthenticated]
    def get(self, request):  # list all active users
        users = User.objects.filter(status='Active') # only active users
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request):# use for creating user and welcome email
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            try:
                send_mail(
                subject='Welcome to Our Platform',
                message=f'Hello {user.first_name}, your account has been created successfully.',
                # from_email="muskan.pathak0506@gmail.com",
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
                status=status.HTTP_201_CREATED # for successful creation
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST # if validation fails then this returns
        )
   

class UserDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk, status='Active')
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_user(pk)  # find active users

        if user is None:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk): # update entire data of user
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

        user.status = 'Inactive' # mark user inactive not delete it
        user.save(update_fields=['status'])

        return Response(
            {"message": "User deactivated successfully"},
            status=status.HTTP_200_OK
        )

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "JWT token verified successfully",
            "user": request.user.email
        })





