from django.contrib.auth import logout
from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from auction.models import Auction
from auction.serializers import AuctionSerializer

from users.mixins import UserQueryMixin
from users.models import User
from users.serializers import LoginSerializer, UserRegisterSerializer, UserSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    # TODO: need to implement saving process for other fields + emails, etc.
    def perform_update(self, serializer) -> User:
        if 'email' in serializer.validated_data:
            raise serializers.ValidationError({
                'email': 'Cannot change email'
            })

        password = serializer.validated_data.pop('password', None)
        user = serializer.save()

        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user

    @transaction.atomic
    def perform_destroy(self, instance: User) -> None:
        instance.deleted = True
        instance.save(update_fields=['deleted'])
        logout(self.request)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
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
