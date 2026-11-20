from auction.models import Auction
from auction.serializers import AuctionSerializer
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.mixins import UserQueryMixin
from users.models import User
from users.serializers import LoginSerializer, UserRegisterSerializer, UserSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ProfileViewSet(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    def perform_update(self, serializer) -> User:
        # The password must never be saved as plain text by ModelSerializer.
        password = serializer.validated_data.pop('password', None)
        user = serializer.save()

        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user

    @transaction.atomic
    def perform_destroy(self, instance: User) -> None:
        # Keep relational integrity, but erase personal data on soft delete.
        instance.email = f"deleted-{instance.pk}@invalid.local"
        instance.username = None
        instance.phone = ''
        instance.avatar = ''
        instance.directional = ''
        instance.deleted = True
        instance.is_active = False
        instance.save(update_fields=[
            'email', 'username', 'phone', 'avatar', 'directional',
            'deleted', 'is_active',
        ])
        logout(self.request)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self) -> QuerySet[User]:
        queryset = User.objects.filter(deleted=False)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.search(search)

        return queryset


class WonAuctionsViewSet(UserQueryMixin, viewsets.ReadOnlyModelViewSet):
    user_field = "winner"

    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = [IsAuthenticated]
