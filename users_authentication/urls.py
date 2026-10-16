from django.urls import path
from .views import LoginAPIView
from .views import SendOTPAPIView
from .views import   VerifyOTPAPIView
from.views import ForgotPasswordAPIView
from.views import  ResetPasswordAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('send-otp/', SendOTPAPIView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    
]






