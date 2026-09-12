from asgiref.sync import async_to_sync
from auction.models import Auction
from channels.layers import get_channel_layer
from django.utils import timezone

from events.events import AuctionEndedEvent, BidPlacedEvent, AuctionStartedEvent, AuctionEndingSoonEvent


def publish_auction_started(event: AuctionStartedEvent):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"auction_{event.auction_id}",
        {
            "type": "auction_started",
            "auction_id": str(event.auction_id),
            "status": event.status,
            "start_price": str(event.start_price),
        }
    )

def publish_auction_ended(event: AuctionEndedEvent):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"auction_{event.auction_id}",
        {
            "type": "auction_ended",
            "auction_id": str(event.auction_id),
            "status": event.status,
            "final_price": str(event.final_price),

        }
    )

def publish_bid_placed(event: BidPlacedEvent):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"auction_{event.auction_id}",
        {
            "type": "bid_placed",
            "auction_id": str(event.auction_id),
            "bid_id": str(event.bid_id),
            "bidder_id": str(event.bidder_id),
            "bid_price": str(event.bid_price),
            "current_price": str(event.current_price),
        },
    )

def publish_bidders_count(auction: Auction):
    channel_layer = get_channel_layer()
    bidders = auction.bids.values("bidder_id").distinct().count()
    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.id}",
        {
            "type": "bidders_count",
            "count": str(bidders),
        }
    )

def publish_auction_ending_soon(event: AuctionEndingSoonEvent):
    channel_layer = get_channel_layer()
    time_to_end = event.end_date - timezone.now()
    seconds_left = max(0, int(time_to_end.total_seconds()))
    async_to_sync(channel_layer.group_send)(
        f"auction_{event.auction_id}",
        {
            "type": "auction_ending_soon",
            "time_to_end": str(seconds_left),
        }
    )
