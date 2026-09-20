from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.permissions.permissions_utils import IsOwnerOfWatchlist

from watchlist.models import Watchlist
from watchlist.serializers.serializers import WatchlistSerializer


class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = (IsOwnerOfWatchlist, IsAuthenticated)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_update(self, serializer) -> None:
        serializer.save()

    @transaction.atomic
    def perform_create(self, serializer: WatchlistSerializer) -> None:
        serializer.save(user=self.request.user)