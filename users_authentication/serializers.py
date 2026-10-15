from rest_framework import serializers

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












