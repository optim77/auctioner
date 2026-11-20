from datetime import datetime
from uuid import UUID

from bid.models import Bid
from django.db.models import QuerySet
from watchlist.models import Watchlist

from auction.models import Auction, AuctionStatus


def get_auction(auction_id: UUID) -> Auction:
    return Auction.objects.with_related().get(id=auction_id)


def get_auction_for_update(auction_id: UUID) -> Auction:
    # Lock only the auction row. ``of=("self",)`` is required because
    # ``winner`` is a nullable FK and PostgreSQL cannot lock the nullable
    # side of an outer join.
    return (
        Auction.objects.select_for_update(of=("self",))
        .select_related("listing", "listing__seller", "winner")
        .get(id=auction_id)
    )


def get_active_auctions() -> QuerySet[Auction]:
    return Auction.objects.is_active().with_related()


def search_auctions(query: str) -> QuerySet[Auction]:
    return Auction.objects.is_active().search(query).newest()


def get_newest_auctions() -> QuerySet[Auction]:
    return Auction.objects.is_active().newest()


def get_newest_auctions_in_category(category: str) -> QuerySet[Auction]:
    return (
        Auction.objects.is_active()
        .filter(listing__category__name__icontains=category)
        .newest()
    )


def get_hot_auctions() -> QuerySet[Auction]:
    return Auction.objects.is_active().hottest()


def get_expired_auction_ids(moment: datetime | None = None) -> QuerySet:
    return Auction.objects.is_active().ended_before(moment).values_list(
        "id", flat=True
    )


def get_auctions_ending_between(start: datetime, end: datetime) -> QuerySet[Auction]:
    return Auction.objects.is_active().ending_between(start, end)


def get_sold_auctions_to_process() -> QuerySet[Auction]:
    return Auction.objects.filter(
        status=AuctionStatus.SOLD,
        processed=False,
        processing=False,
        winner__isnull=False,
    )


def get_watchlist_user_ids(auction_id: UUID) -> QuerySet:
    return (
        Watchlist.objects.filter(
            auction_id=auction_id,
            notifications_enabled=True,
        )
        .values_list("user_id", flat=True)
        .distinct()
    )


def get_bidder_ids(auction_id: UUID) -> QuerySet:
    return (
        Bid.objects.filter(auction_id=auction_id)
        .values_list("bidder_id", flat=True)
        .distinct()
    )
