from rest_framework import serializers
from .models import User, Client, Project
from .utils import generate_unique_username

class UserSerializer(serializers.ModelSerializer):
    profiles = serializers.CharField(required=False,max_length=50)
    gender = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    blood_group = serializers.CharField( required=False,allow_blank=True,allow_null=True)
    status = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    user_name = serializers.CharField(required=False,allow_blank=True,allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'user_name',
            'email',
            'password',
            'profiles',
            'date_of_birth',
            'gender',
            'nationality',
            'image',
            'blood_group',
            'phone',
            'permanent_address',
            'current_address',
            'emergency_contact_name',
            'emergency_contact_number',
            'emergency_contact_relationship',
            'status',
        ] 
        extra_kwargs = {
        'email': {
            'required': True,
            'allow_blank': False,
        },
         'password': {
        'required': False,
        'write_only': True,
    },
    }

    def validate_profiles(self, value):
        value = value.strip()

        for option, _label in User.Profile_Choices: # for case insensitivity like developer becomes Developer
            if value.casefold() == option.casefold():
                return option
        return value



    def create(self, validated_data):
        validated_data.pop('password', None)
        email = validated_data['email']

        validated_data['username'] = generate_unique_username(email)

        user = User(**validated_data)
        user.set_password(f"{email.split('@')[0]}@123")
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        required = False
    )


class SendOTPSerializer(serializers.Serializer):  # validate krega email ko
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer): # email and otp dono ko validate krega
    email = serializers.EmailField()
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=False
    )


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()  # jiska password reset krna h uska email
    otp = serializers.RegexField(regex=r'^\d{6}$')
    new_password = serializers.CharField(
        write_only=True,  # new password api mai show nhi hoga
        min_length=8,
        trim_whitespace=False
    )

class ClientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, allow_blank=False, allow_null=False
    )

    class Meta:
        model = Client
        fields = [
            'id',
            'first_name',
            'last_name',
            'address',
            'country',
            'contact_number',
            'email',
            'status',
            'created_at',
            'created_by',
            'modified_at',
            'modified_by',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'created_by',
            'modified_at',
            'modified_by',
        ]

    def validate_status(self, value):
        if not isinstance(value, str):
            return value

        value = value.strip().casefold()

        for choice_value, choice_label in Client.STATUS_CHOICES:
            if value == choice_value.casefold():
                return choice_value

        raise serializers.ValidationError(
            "Status must be Active or Inactive."
        )

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields =['id', 'project_title', 'project_type', 'date_of_completion', 'project_status', 'client', 'manager',
          'created_at', 'created_by', 'modified_at', 'modified_by']

        read_only_fields = ['id','created_at','created_by','modified_at','modified_by']

    # def validate_project_type(self, value):
    #     if value is None:
    #         return value
    #     value = value.strip()
    #     for option, _label in Project.PROJECT_TYPE_CHOICE: # for case insensitivity
    #         if value.casefold() == option.casefold():
    #             return option
    #     return value

    # def validate_project_type(self, value):
    #     if value is None:
    #         return value

    #     # CHANGE: beech ke extra spaces bhi hatao ("AI   Project" -> "AI Project")
    #     value = " ".join(value.split())

    #     # 1. Default options se case-insensitive match
    #     for option, _label in Project.PROJECT_TYPE_CHOICE:
    #         if value.casefold() == option.casefold():
    #             return option

    #     # CHANGE: 2. Database mein pehle se saved types se match (ai project -> AI Project)
    #     saved_types = Project.objects.exclude(project_type__isnull=True).values_list('project_type', flat=True).distinct()
    #     for saved in saved_types:
    #         if saved and value.casefold() == saved.casefold():
    #             return saved

    #     # 3. Bilkul naya type, jaisa likha waisa save hoga
    #     return value
    

    def validate(self, attrs):
        required_fields = ['project_title', 'project_type', 'client', 'manager']

        for field in required_fields:
            if self.instance is not None and field not in attrs:
                continue

            value = attrs.get(field)
            if value is None:
                raise serializers.ValidationError({field: f'{field} is required.'})

            if field in ['project_title', 'project_type'] and not value.strip():
                raise serializers.ValidationError({field: f'{field} is required.'})
            
        client = attrs.get('client') # inactive client ya manager allowed nhi h
        if client is not None and client.status != 'Active':
            raise serializers.ValidationError({'client': 'Client is not active.'})

        manager = attrs.get('manager')
        if manager is not None and manager.status != 'Active':
            raise serializers.ValidationError({'manager': 'Manager is not active.'})

        return attrs
                    
                    
            
                    
                    
                
                  
                    





















