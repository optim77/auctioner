from django.db import transaction
from users.models import User

from watchlist.models import Watchlist


class WatchlistService:
    """Write-side operations for watchlist entries."""

    @staticmethod
    @transaction.atomic
    def create_entry(data: dict, user: User) -> Watchlist:
        """Create a watchlist entry, always owned by the requesting user."""
        data = {key: value for key, value in data.items() if key != "user"}
        return Watchlist.objects.create(**data, user=user)

    @staticmethod
    @transaction.atomic
    def update_entry(entry: Watchlist, data: dict, user: User) -> Watchlist:
        """Update a watchlist entry, keeping it owned by the requesting user."""
        for field, value in data.items():
            if field != "user":
                setattr(entry, field, value)
        entry.user = user
        entry.save()
        return entry


WatchlistServices = WatchlistService
