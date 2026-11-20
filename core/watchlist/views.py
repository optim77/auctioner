from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from watchlist.models import Watchlist
from watchlist.permissions import IsOwnerOfWatchlist
from watchlist.selectors import get_user_watchlist
from watchlist.serializers import WatchlistSerializer
from watchlist.services import WatchlistService


class WatchlistViewSet(viewsets.ModelViewSet):
    """CRUD interface for the requesting user's watchlist."""

    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = (IsOwnerOfWatchlist, IsAuthenticated)

    def get_queryset(self):
        return get_user_watchlist(self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.instance = WatchlistService.create_entry(
            serializer.validated_data, self.request.user
        )

    def perform_update(self, serializer) -> None:
        WatchlistService.update_entry(
            serializer.instance, serializer.validated_data, self.request.user
        )
