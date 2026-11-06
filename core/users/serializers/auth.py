from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Wrong email or password")
        if not user.is_active:
            raise serializers.ValidationError("Inactive user")
        attrs['user'] = user
        return attrs
