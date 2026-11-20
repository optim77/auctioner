import logging

from asgiref.sync import async_to_sync
from auction.models import Auction
from channels.layers import get_channel_layer
from django.utils import timezone

from events.ws.events import (
    AuctionEndedEvent,
    AuctionEndingSoonEvent,
    AuctionStartedEvent,
    BidPlacedEvent,
)

logger = logging.getLogger(__name__)


def _group_send(group_name: str, payload: dict) -> None:
    """Send to a channel group without letting transport errors escape.

    These calls often run from ``transaction.on_commit`` callbacks. An
    unavailable Redis used to raise there (breaking the request/worker thread)
    even though the database change itself had already succeeded.
    """
    try:
        async_to_sync(get_channel_layer().group_send)(group_name, payload)
    except Exception:
        logger.exception("Failed to publish websocket event to %s", group_name)


def publish_auction_started(event: AuctionStartedEvent) -> None:
    _group_send(
        f"auction_{event.auction_id}",
        {
            "type": "auction_started",
            "auction_id": str(event.auction_id),
            "status": event.status,
            "start_price": str(event.start_price),
        },
    )


def publish_auction_ended(event: AuctionEndedEvent) -> None:
    _group_send(
        f"auction_{event.auction_id}",
        {
            "type": "auction_ended",
            "auction_id": str(event.auction_id),
            "status": event.status,
            "final_price": str(event.final_price),
        },
    )


def publish_bid_placed(event: BidPlacedEvent) -> None:
    _group_send(
        f"auction_{event.auction_id}",
        {
            "type": "bid_placed",
            "auction_id": str(event.auction_id),
            "bid_id": str(event.bid_id),
            "bid_price": str(event.bid_price),
            "current_price": str(event.current_price),
        },
    )


def publish_bidders_count(auction: Auction) -> None:
    bidders = auction.bids.values("bidder_id").distinct().count()
    _group_send(
        f"auction_{auction.id}",
        {
            "type": "bidders_count",
            "count": str(bidders),
        },
    )


def publish_auction_ending_soon(event: AuctionEndingSoonEvent) -> None:
    time_to_end = event.end_date - timezone.now()
    seconds_left = max(0, int(time_to_end.total_seconds()))
    _group_send(
        f"auction_{event.auction_id}",
        {
            "type": "auction_ending_soon",
            "time_to_end": str(seconds_left),
        },
    )
