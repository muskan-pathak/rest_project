from django.urls import path
from .views import UserListCreateAPI, UserDetailAPI, ClientListCreateAPI,ClientDetailAPI


urlpatterns = [
    path('users/', UserListCreateAPI.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),
    path('clients/', ClientListCreateAPI.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailAPI.as_view(), name='client-detail'),
]












