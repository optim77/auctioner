from asgiref.sync import async_to_sync
from auction.models import Auction
from channels.layers import get_channel_layer
from django.utils import timezone

from bid.models import Bid


def publish_auction_started(auction: Auction):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.id}",
        {
            "type": "auction_started",
            "auction_id": str(auction.id),
            "status": auction.status,
            "start_price": str(auction.start_price),
        }
    )

def publish_auction_ended(auction: Auction):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.id}",
        {
            "type": "auction_ended",
            "auction_id": str(auction.id),
            "status": auction.status,
            "final_price": str(auction.final_price),

        }
    )

def publish_bid_placed(bid: Bid):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"auction_{bid.auction.id}",
        {
            "type": "bid_placed",
            "auction_id": str(bid.auction.id),
            "bid_id": str(bid.id),
            "bidder_id": str(bid.bidder.id),
            "bid_price": str(bid.bid_price),
            "current_price": str(bid.auction.current_price),
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

def publish_auction_ending_soon(auction: Auction):
    channel_layer = get_channel_layer()
    time_to_end = auction.end_date - timezone.now()
    seconds_left = max(0, int(time_to_end.total_seconds()))
    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.id}",
        {
            "type": "auction_ending_soon",
            "time_to_end": str(seconds_left),
        }
    )
