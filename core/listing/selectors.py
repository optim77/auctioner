from django.db.models import QuerySet

from auction.models import Auction
from users.models import User


def get_user_listings(user: User) -> QuerySet:
    auctions = Auction.objects.filter(user=user, is_active=True)
    return auctions
