from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Wrong email or password")
        if not user.is_active or user.deleted:
            raise serializers.ValidationError("Wrong email or password")
        attrs['user'] = user
        return attrs
