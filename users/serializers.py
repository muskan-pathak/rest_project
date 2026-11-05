from rest_framework import serializers
from .models import User, Profile, Client, Project,ProjectAttachment
from .utils import generate_unique_username
from django.db import transaction

class ProfileIdOrNameField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, bool):
            raise serializers.ValidationError(
                "Enter a valid profile ID or profile name."
            )

        if isinstance(data, int) or (
            isinstance(data, str) and data.strip().isdigit()
        ):
            try:
                return Profile.objects.get(pk=int(data))
            except Profile.DoesNotExist:
                raise serializers.ValidationError(
                    "Profile with this ID does not exist."
                )

        if isinstance(data, str) and data.strip():
            profile = Profile.objects.filter(
                name__iexact=data.strip()
            ).first()

            if profile is not None:
                return profile

            raise serializers.ValidationError(
                "Profile with this name does not exist."
            )

        raise serializers.ValidationError(
            "Enter a valid profile ID or profile name."
        )

    def to_representation(self, value):
        return value.pk



class UserSerializer(serializers.ModelSerializer):
    # profile = ProfileIdOrNameField(
    #     queryset=Profile.objects.all(),
    #     required=False,
    #     allow_null=True)
    profile = serializers.PrimaryKeyRelatedField(
    queryset=Profile.objects.all(),required=True,allow_null=False)


    profile_details = serializers.SerializerMethodField(read_only=True)
    profile_details = serializers.SerializerMethodField(read_only=True)     
    gender = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    blood_group = serializers.CharField( required=False,allow_blank=True,allow_null=True)
    status = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    user_name = serializers.CharField(required=False,allow_blank=True,allow_null=True)

    class Meta:
        model = User
        fields = ['id','first_name','last_name','user_name','email','password', 'profile',
        'profile_details','date_of_birth','gender', 'nationality','image','blood_group',
        'phone','permanent_address','current_address','emergency_contact_name','emergency_contact_number',
        'emergency_contact_relationship','status',]
    
        extra_kwargs = {
            'email': {'required': True,'allow_blank': False,},
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

    
    def get_profile_details(self, obj):
        if obj.profile is None:
            return None

        return {
            'id': obj.profile.id,
            'name': obj.profile.name,
            'is_default': obj.profile.is_default,
        }

    def create(self, validated_data):
        profile = validated_data.pop('profile', None)

        email = validated_data['email']
        validated_data['username'] = generate_unique_username(email)

        if profile is None:
            profile = Profile.objects.filter(is_default=True).first()

        user = User(**validated_data)
        user.profile = profile
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



class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'name', 'is_default']
        read_only_fields = ['is_default']

    SYSTEM_PROFILES = [
        'Super Admin',
        'Admin',
        'Manager',
        'Team Leader',
        'Developer',
        'Human Resource',
    ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Profile name cannot be empty."
            )

        queryset = Profile.objects.filter(name__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A profile with this name already exists."
            )

        return value

    def create(self, validated_data):
        name = validated_data['name']

        validated_data['is_default'] = (
            name.casefold() in
            [profile.casefold() for profile in self.SYSTEM_PROFILES]
        )

        return Profile.objects.create(**validated_data)

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
    created_by = serializers.SerializerMethodField()
    modified_by = serializers.SerializerMethodField()
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        allow_null=False
    )

    class Meta:
        model = Client
        fields = ['id','first_name','last_name','address','country','contact_number','email',
                  'status','created_at','created_by','modified_at','modified_by',]
 
        read_only_fields = ['id','created_at','created_by','modified_at','modified_by',]     

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
    
    def get_created_by(self, obj):
        if obj.created_by is None:
            return None
        profile = None
        if obj.created_by.profile is not None:
            profile = {
                'id': obj.created_by.profile.id,
                'name': obj.created_by.profile.name
            }

        return {
            'id': obj.created_by.id,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
            'email': obj.created_by.email,
            'profile': profile
        }

    def get_modified_by(self, obj):
        if obj.modified_by is None:
            return None
        profile = None
        if obj.modified_by.profile is not None:
            profile = {
                'id': obj.modified_by.profile.id,
                'name': obj.modified_by.profile.name
            }

        return {
            'id': obj.modified_by.id,
            'first_name': obj.modified_by.first_name,
            'last_name': obj.modified_by.last_name,
            'email': obj.modified_by.email,
            'profile': profile
        }

class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    modified_by = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField(read_only=True)
    # client = serializers.SerializerMethodField()
    # manager = serializers.SerializerMethodField()
     # attached file ki details response mai show krne ke liye

    new_attachments = serializers.ListField( # list field  use so that multiple file  can be uploaded
        child=serializers.FileField(), 
        required=False,
        write_only=True
    )

    delete_attachment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Project
        fields = ['id','project_title','project_type','description','attachments','date_of_completion','project_status',
                  'client','manager','created_at','created_by','modified_at','modified_by',
                  'new_attachments','delete_attachment_ids', ] 
       
        read_only_fields = ['id','created_at','created_by','modified_at','modified_by','attachments',]

      # client/manager input me id, output me id/first_name/last_name/email
    # def to_representation(self, instance):
    #     data= super().to_representation(instance)
    #     for field in ['client','manager']:
    #         obj= getattr(instance, field)
    #         if obj is None:
    #             data[field]= None
    #         else:
    #             data[field]= {"id": obj.id, "first_name": obj.first_name, "last_name": obj.last_name, "email": obj.email}
    #     return data   
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Client details
        if instance.client is None:
            data['client'] = None
        else:
            data['client'] = {
                "id": instance.client.id,
                "first_name": instance.client.first_name,
                "last_name": instance.client.last_name,
                "email": instance.client.email
            }

        # Manager details
        if instance.manager is None:
            data['manager'] = None
        else:
            data['manager'] = {
                "id": instance.manager.id,
                "profile_id": instance.manager.profile.id if instance.manager.profile else None,
                "first_name": instance.manager.first_name,
                "last_name": instance.manager.last_name,
                "email": instance.manager.email
            }

        return data

    
    def validate(self, attrs):
        required_fields = ['project_title', 'project_type', 'manager']

        for field in required_fields:
            if self.instance is not None and field not in attrs:
                continue

            value = attrs.get(field)

            if value is None:
                raise serializers.ValidationError({
                    field: f'{field} is required.'
                })

            if field in ['project_title', 'project_type'] and not value.strip():
                raise serializers.ValidationError({
                    field: f'{field} is required.'
                })

        client = attrs.get('client')
        if client is not None and client.status != 'Active':
            raise serializers.ValidationError({
                'client': 'Client is not active.'
            })

        manager = attrs.get('manager')

        if manager is not None:
            if manager.status != 'Active':
                raise serializers.ValidationError({
                    'manager': 'Manager is not active.'
                })

            if manager.profile is None or manager.profile.name.casefold() != 'manager':
                raise serializers.ValidationError({
                    'manager': 'Only users with Manager profile can be assigned as project manager.'
                })

        # manager = attrs.get('manager')
        # if manager is not None and manager.status != 'Active':
        #     raise serializers.ValidationError({
        #         'manager': 'Manager is not active.'
        #     })

        return attrs

    def get_created_by(self, obj):
        if obj.created_by is None:
            return None
        profile = None
        if obj.created_by.profile is not None:
            profile = {
                'id': obj.created_by.profile.id,
                'name': obj.created_by.profile.name
            }

        return {
            'id': obj.created_by.id,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
            'email': obj.created_by.email,
            'profile': profile
            
        }

    def get_modified_by(self, obj):
        if obj.modified_by is None:
            return None

        profile = None
        if obj.modified_by.profile is not None:
            profile = {
                'id': obj.modified_by.profile.id,
                'name': obj.modified_by.profile.name
            }

        return {
            'id': obj.modified_by.id,
            'first_name': obj.modified_by.first_name,
            'last_name': obj.modified_by.last_name,
            'email': obj.modified_by.email,
            'profile': profile
        }
            
        

    # def get_client(self, obj):
    #     if obj.client is None:
    #         return None

    #     return {
    #         'id': obj.client.id,
    #         'first_name': obj.client.first_name,
    #         'last_name': obj.client.last_name,
    #         'email': obj.client.email,
    #     }


    # def get_manager(self, obj):
    #     if obj.manager is None:
    #         return None

    #     return {
    #         'id': obj.manager.id,
    #         'first_name': obj.manager.first_name,
    #         'last_name': obj.manager.last_name,
    #         'email': obj.manager.email,
    #     }

    def get_attachments(self, obj):
        attachments = obj.attachments.all() # get all attachment of current project

        if not attachments.exists():
            return None

        return ProjectAttachmentSerializer(
            attachments,
            many=True,
            context=self.context
        ).data # serializer ke serialized output ko access krne ke liye

    @transaction.atomic # database transaction ko ensure krne ke liye ki agar koi error aata h to sab changes rollback ho jaye
    def create(self, validated_data):
        new_attachments = validated_data.pop('new_attachments', [])
        validated_data.pop('delete_attachment_ids', [])

        request = self.context.get('request')
        user = request.user if request else None

        project = Project.objects.create(
            created_by=user,
            modified_by=user,
            **validated_data #** dictionary unpacking
        )

        for file in new_attachments:
            ProjectAttachment.objects.create(
                project=project,
                file=file,
                file_name=file.name,
                # uploaded_by=user,
                # modified_by=user
            )

        return project

    @transaction.atomic
    def update(self, instance, validated_data):
        new_attachments = validated_data.pop('new_attachments', []) # new attachment retrieve kr rhe h
        delete_attachment_ids = validated_data.pop(
            'delete_attachment_ids', []
        )

        request = self.context.get('request')
        user = request.user if request else None

        # Check that requested attachment IDs belong to this project
        if delete_attachment_ids: # check kr rhe h ki delete_attachment_ids empty h ya nhi
            attachments_to_delete = instance.attachments.filter(
                id__in=delete_attachment_ids
            )

            found_ids = set(
                attachments_to_delete.values_list('id', flat=True)
            )
            requested_ids = set(delete_attachment_ids)

            if found_ids != requested_ids:
                raise serializers.ValidationError({
                    'delete_attachment_ids':
                    'One or more attachment IDs do not belong to this project.'
                })

            attachments_to_delete.delete()

        # Update project fields
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        instance.modified_by = user
        instance.save()

        # Add new attachments
        for file in new_attachments:
            ProjectAttachment.objects.create(
                project=instance,
                file=file,
                file_name=file.name,
                uploaded_by=user,
                modified_by=user
            )

        return instance


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    # uploaded_by = serializers.SerializerMethodField()
    # modified_by = serializers.SerializerMethodField()
    class Meta:
        model = ProjectAttachment
        fields = ['id', 'file', 'file_name']

        read_only_fields = ['id']

    # def get_uploaded_by(self, obj):
    #     if obj.uploaded_by is None:
    #         return None

    #     return {
    #         'first_name': obj.uploaded_by.first_name,
    #         'last_name': obj.uploaded_by.last_name,
    #         'email': obj.uploaded_by.email,
    #     }

    # def get_modified_by(self, obj):
    #     if obj.modified_by is None:
    #         return None

    #     return {
    #         'first_name': obj.modified_by.first_name,
    #         'last_name': obj.modified_by.last_name,
    #         'email': obj.modified_by.email,
    #     }




    



                    
                    
    










                    
                    
            
                    
                    
                
                  
                    





















