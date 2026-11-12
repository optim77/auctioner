from django.db.models import QuerySet

from listing.models import Listing
from users.models import User


def get_user_listings(user: User) -> QuerySet[Listing]:
    """Return all listings owned by the given user."""
    return Listing.objects.select_related('category').filter(seller=user)
