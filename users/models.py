from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.utils.field_mapping import get_field_kwargs


class User(AbstractUser):
    email = models.EmailField(unique = True, null=True, blank=True)
    user_name = models.CharField(max_length=100,unique= True, null = True, blank = True)
    first_name = models.CharField(max_length=100,null = True, blank = True)
    last_name = models.CharField(max_length=100,null = True, blank = True)

    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),]

    Blood_Group_Choices = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),]          

    Status_Choices = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),]

    profile = models.ForeignKey(
    'Profile',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='users')


    
    # profiles = models.CharField(max_length=52,choices=Profile_Choices,default='Standard',null=True,blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=12, choices=gender_choices, blank = True, null= True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/',null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices= Blood_Group_Choices, blank=True,null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null= True)
    current_address = models.TextField(blank=True,null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True,null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True,null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField("password", max_length=128, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status_Choices, default='Active',blank=True, null=True)
    otp_hash = models.CharField(max_length=128, blank=True, null=True) 
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_is_used = models.BooleanField(default=False,null=True, blank=True)
    otp_request_count = models.PositiveIntegerField(default=0,null=True, blank=True)
    otp_request_window_start = models.DateTimeField(null= True, blank = True)
    otp_blocked_until = models.DateTimeField(null = True, blank= True)

    def __str__(self):
        return self.email
    
class Profile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return self.name
    
class Client(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),]
    first_name = models.CharField(max_length=100, null= True, blank= True)
    last_name = models.CharField(max_length=100, null= True, blank= True)
    address = models.TextField(null= True, blank= True)
    country = models.CharField(max_length=100, null= True, blank= True)
    contact_number = models.CharField(max_length=15, null= True, blank= True)
    email = models.EmailField(unique=True,null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True) # auto now automatically save kr leta h date and time at the time of creation
    created_by = models.ForeignKey(  # relation b/W user and client model 
        'User',on_delete=models.PROTECT,         # if i as a user create a client then my reference save in client model  
        related_name='created_clients',
        null=True, blank=True
    )
    modified_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    modified_by = models.ForeignKey(
        'User',on_delete=models.PROTECT,null=True, blank=True,
        related_name='modified_clients' # help in retrieve the client modiefied by the user lastly
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Project(models.Model):
    PROJECT_TYPE_CHOICE = [
        ('Web Development','Web Development'),
        ('Mobile App', 'Mobile App'),
        ('Software', 'Software'),
        ('Design','Design'),]
    
    PROJECT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),]
    
    project_title = models.CharField(max_length= 100,null=True, blank=True)
    project_type = models.CharField(max_length=50,null=True, blank=True)
    description = models.TextField(null = True,blank=True)
    start_date = models.DateField(auto_now_add=True, null=True, blank=True)
    date_of_completion = models.DateField(null=True, blank=True)
    project_status = models.CharField(max_length=42,choices=PROJECT_STATUS_CHOICES,default='In Progress',
        null=True, blank=True)
    
    client = models.ForeignKey( # project kis client ke liye h
        'Client',on_delete=models.PROTECT,related_name='projects',null=True, blank=True)
    manager = models.ForeignKey( # project ka manager (in user)
        'User',on_delete=models.PROTECT,related_name='managed_projects',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='created_projects',
        null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    modified_by = models.ForeignKey('User',on_delete=models.PROTECT,related_name='modified_projects',
        null=True, blank=True) 
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.project_title}"


class ProjectAttachment(models.Model):
    project = models.ForeignKey('Project',on_delete=models.CASCADE,related_name="attachments")
    file = models.FileField(upload_to='project_attachments/')
    file_name = models.CharField(max_length=250,null=True,blank=True)


    def __str__(self):
        return self.file.name



class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),]
    
    project = models.ForeignKey('Project',on_delete=models.PROTECT,related_name='tasks',null=True,blank=True)
    assign_by = models.ForeignKey('User',on_delete=models.PROTECT,related_name='assigned_by_tasks',null=True,blank=True)            
    assign_to = models.ForeignKey('User',on_delete=models.PROTECT,related_name='assigned_tasks',null=True,blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending',null=True,blank=True)
    task_start_date = models.DateField(auto_now_add=True,null=True, blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    # restore_by = models.ForeignKey('User',on_delete=models.PROTECT,related_name='restored_tasks',null=True,blank=True) 
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey('User',on_delete=models.PROTECT,related_name='created_tasks',null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey('User',on_delete=models.PROTECT,related_name='updated_tasks',null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['project', 'title'],name='unique_task_title_per_project')]
              
    def __str__(self):
        return self.title or f"Task {self.id}"


class TaskComment(models.Model):
    task = models.ForeignKey('ProjectTask',on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey('User',on_delete=models.PROTECT,related_name='task_comments')
    comment = models.TextField(null=True,blank=True)
    def __str__(self):
        return f"Comment on Task {self.task_id} by {self.user_id}"


















            
        








