from rest_framework import serializers
from .models import User, Client

class UserSerializer(serializers.ModelSerializer):
    profiles = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    gender = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    blood_group = serializers.CharField( required=False,allow_blank=True,allow_null=True)
    status = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    user_name = serializers.CharField(required=False,allow_blank=True,allow_null=True)
    # password = serializers.CharField(required=False,allow_blank=True,allow_null=True)

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
    
    
    # def normalize_choice(self, value, choices, field_name):
    #     if not isinstance(value, str):
    #         return value

    #     value = value.strip().casefold()

    #     for choice_value, choice_label in choices:
    #         if value == choice_value.casefold():
    #             return choice_value

    #     raise serializers.ValidationError({
    #         field_name: "Invalid choice."
    #     })

    # def validate_status(self, value):
    #     return self.normalize_choice(
    #         value, User.Status_Choices, "status"
    #     )

    # def validate_gender(self, value):
    #     return self.normalize_choice(
    #         value, User.gender_choices, "gender"
    #     )

    # def validate_blood_group(self, value):
    #     return self.normalize_choice(
    #         value, User.Blood_Group_Choices, "blood_group"
    #     )

    # def validate_profiles(self, value):
    #     return self.normalize_choice(
    #         value, User.Profile_Choices, "profiles"
    #     )


    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     user = User(**validated_data)
    #     user.set_password(password)
    #     user.save()
    #     return user
    def create(self, validated_data):
        validated_data.pop('password', None)
        user = User(**validated_data)
        user.set_unusable_password()
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
        trim_whitespace=False
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



















