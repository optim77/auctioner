from django.db.models import Q, QuerySet

from auction.models import Auction


def get_newest_auction_in_category(category: str) -> QuerySet[Auction]:
    return Auction.objects.is_active().filter(listing__category__name__icontains=category)

def search_auction(query: str) -> QuerySet[Auction]:
    lookup = Q(listing__name__icontains=query) | Q(listing__description__icontains=query)
    return Auction.objects.is_active().filter(lookup).order_by("-created_at")[:10]

def newest_auction() -> QuerySet[Auction]:
    return Auction.objects.is_active().order_by("-bids_counter")[:10]

def newest_auction_in_category(*, category: str) -> QuerySet[Auction]:
    lookup = Q(listing__category__name__icontains=category)
    return Auction.objects.is_active().filter(lookup).order_by("-created_at")[:10]

def get_hot_auctions() -> QuerySet[Auction]:
    return Auction.objects.order_by("-bids_counter")