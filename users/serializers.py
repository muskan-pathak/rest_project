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
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user













