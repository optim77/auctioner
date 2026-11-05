from django.db.models import QuerySet

from users.models import User
from watchlist.models import Watchlist


def get_user_watchlist(user: User) -> QuerySet:
    """All watchlist entries belonging to the given user."""
    return Watchlist.objects.filter(user=user)
