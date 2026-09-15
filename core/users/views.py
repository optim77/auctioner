from django.contrib.auth import logout
from django.db import transaction
from rest_framework import viewsets, generics, status, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from users.permissions.permissions_utils import IsAccountOwner
from users.models import User
from users.serializers.serializers import LoginSerializer, UserRegisterSerializer, UserSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserViewSet(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # TODO: need to implement saving process for other fields + emails, etc.
    def perform_update(self, serializer):
        user = serializer.instance
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.pop('password', None)

        if email is not None:
            raise serializers.ValidationError({
                'email': 'Cannot change email'
            })

        if password:
            user.set_password(password)

        serializer.save()

        if password:
            user.save(update_fields=['password'])
        return user

    @transaction.atomic
    def perform_destroy(self, request, instance: User):
        instance.deleted = True
        instance.save(update_fields=['deleted'])
        logout(request)
