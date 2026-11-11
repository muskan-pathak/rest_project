from django.urls import path
from .views import (UserListCreateAPI,UserDetailAPI,LoginAPIView,SendOTPAPIView,VerifyOTPAPIView,ForgotPasswordAPIView,ResetPasswordAPIView,
ClientListCreateAPI, ClientDetailAPI,ProjectListCreateAPI,ProjectDetailAPI,ProfileListCreateView,
ProfileDetailView,ProfileUsersByIdView,ProfileUsersByNameView,RestoreUserAPI,RestoreClientAPI,RestoreProjectAPI,ProjectTaskListCreateAPI,ProjectTaskDetailAPI,TaskCommentListCreateAPI,TaskCommentDetailAPI)  

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
    path('projects/<int:pk>/', ProjectDetailAPI.as_view(), name='project-detail'),
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/by-name/<str:profile_name>/users/', ProfileUsersByNameView.as_view(), name='profile-users-by-name'),
    path('profiles/<int:profile_id>/users/', ProfileUsersByIdView.as_view(), name='profile-users-by-id'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('projects/<int:pk>/attachments/<int:attachment_id>/',ProjectDetailAPI.as_view(),
    name='project-attachment-delete'),
    path('users/restore/',RestoreUserAPI.as_view(),name='restore-users'),
    path('users/restore/<str:ids>/',RestoreUserAPI.as_view(),name='restore-users-by-ids'),
    path('clients/restore/<str:ids>/',RestoreClientAPI.as_view(),name='restore-clients-by-ids'),
    path('clients/restore/',RestoreClientAPI.as_view(),name='restore-clients'),
    path('projects/restore/',RestoreProjectAPI.as_view(),name='restore-projects'),
    path('projects/restore/<str:ids>/',RestoreProjectAPI.as_view(),name='restore-projects-by-ids'),
    path('project-tasks/',ProjectTaskListCreateAPI.as_view(),name='project-task-list-create'),
    path('project-tasks/<int:pk>/',ProjectTaskDetailAPI.as_view(),name='project-task-detail'),
    path('task-comments/',TaskCommentListCreateAPI.as_view(),name='task-comments'),
    path('task-comments/<int:pk>/', TaskCommentDetailAPI.as_view(), name='task-comment-detail'),
    
    
    

    
    
    
    

    
    
    

    

    

    
    
    
]   
    

    
    
   



    
    
    


    
    



   



























