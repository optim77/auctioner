from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_staff', 'is_active', 'role', 'password']
