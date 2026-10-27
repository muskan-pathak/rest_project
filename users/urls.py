from django.urls import path
from .views import UserListCreateAPI, UserDetailAPI, LoginAPIView, SendOTPAPIView,VerifyOTPAPIView, ForgotPasswordAPIView, ResetPasswordAPIView, ClientListCreateAPI,ClientDetailAPI,ProjectListCreateAPI, ProjectDetailAPI


urlpatterns = [
    path('users/', UserListCreateAPI.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/send-otp/', SendOTPAPIView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('clients/', ClientListCreateAPI.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailAPI.as_view(), name='client-detail'),
    path('projects/', ProjectListCreateAPI.as_view(), name='project-list-create'),
    # path('projects/types/', ProjectTypeListAPI.as_view(), name='project-types'),
    path('projects/<int:pk>/', ProjectDetailAPI.as_view(), name='project-detail'),


]




















