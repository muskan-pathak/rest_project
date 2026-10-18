from django.urls import path
from .views import UserListCreateAPI, UserDetailAPI, ProtectedAPIView

urlpatterns = [
    path('users/', UserListCreateAPI.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),
    path('protected/', ProtectedAPIView.as_view(), name='protected-api'),
]







