from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from auction.models import Auction


def publish_price_changed(auction: Auction):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.id}",
        {
            "type": "price_changed",
            "auction_id": str(auction.id),
            "current_price": str(auction.current_price),
        },
    )