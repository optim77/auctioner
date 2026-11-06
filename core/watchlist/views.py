from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from watchlist.models import Watchlist
from watchlist.permissions import IsOwnerOfWatchlist
from watchlist.selectors import get_user_watchlist
from watchlist.serializers import WatchlistSerializer
from watchlist.services import WatchlistServices


class WatchlistViewSet(viewsets.ModelViewSet):
    """CRUD interface for the requesting user's watchlist."""

    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsOwnerOfWatchlist, IsAuthenticated)

    def get_queryset(self):
        return get_user_watchlist(self.request.user)

    def perform_create(self, serializer) -> None:
        WatchlistServices.create_entry(serializer, self.request.user)

    def perform_update(self, serializer) -> None:
        WatchlistServices.update_entry(serializer, self.request.user)
