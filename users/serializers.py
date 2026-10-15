from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
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
            'password': {
                'write_only': True,
                'required': True,
                'min_length': 8,
            },
            'email': {
                'required': True,
            },
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
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
















