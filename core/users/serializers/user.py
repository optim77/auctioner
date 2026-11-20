from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'date_joined',
            'is_staff',
            'is_active',
            'role',
            'password',
            'phone',
            'avatar',
            'directional',
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff', 'is_active', 'role']

    def validate_email(self, value: str) -> str:
        if self.instance is not None and self.instance.email != value:
            raise serializers.ValidationError('Cannot change email')
        return value

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value, user=self.instance)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value
