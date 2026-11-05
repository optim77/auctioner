from rest_framework.serializers import BaseSerializer

from django.db import transaction

from users.models import User
from watchlist.models import Watchlist


class WatchlistServices:

    @staticmethod
    @transaction.atomic
    def create_entry(serializer: BaseSerializer, user: User) -> Watchlist:
        """Create a watchlist entry, always owned by the requesting user."""
        return serializer.save(user=user)

    @staticmethod
    @transaction.atomic
    def update_entry(serializer: BaseSerializer, user: User) -> Watchlist:
        """Update a watchlist entry, keeping it owned by the requesting user."""
        return serializer.save(user=user)
