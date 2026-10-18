from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique = True)

    Profile_Choices = [
            ('Administrator', 'Administrator'),
            ('Standard', 'Standard'),
            ('Developer', 'Developer'),
            ('Client', 'Client'),
            ('Human Resource', 'Human Resource'),
        ]
    gender_choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),

    ]

    Blood_Group_Choices = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
                

    Status_Choices = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),

    ]
    profiles = models.CharField(max_length=20, choices=Profile_Choices, default='Standard')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=12, choices=gender_choices, blank = True)
    nationality = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_images/',null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices= Blood_Group_Choices, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    permanent_address = models.TextField(blank=True)
    current_address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=Status_Choices, default='Active')
    otp_hash = models.CharField(max_length=128, blank=True, null=True) 
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_is_used = models.BooleanField(default=False)




    def __str__(self):
        return self.email
            
        








