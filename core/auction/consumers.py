from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from auction.models import Auction


class AuctionConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.auction_id = None

    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.group_name = f"auction_{self.auction_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        auction = await self.get_auction()

        await self.send_json({
            "type": "auction_state",
            "auction_id": str(auction.id),
            "status": auction.status,
            "current_price": str(auction.current_price),
            "end_date": auction.end_date.isoformat(),
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def auction_started(self, event):
        await self.send_json({
            "type": "auction_started",
            "auction_id": event["auction_id"],
            "status": event["status"],
            "start_price": event["start_price"],
        })

    async def auction_ended(self, event):
        await self.send_json({
            "type": "auction_ended",
            "auction_id": event["auction_id"],
            "status": event["status"],
            "final_price": event["final_price"],
        })

    async def bid_placed(self, event):
        await self.send_json({
            "type": "bid_placed",
            "auction_id": event["auction_id"],
            "bid_id": event["bid_id"],
            "bidder_id": event["bidder_id"],
            "bid_price": event["bid_price"],
            "current_price": event["current_price"],
        })

    async def bidders_count(self, event):
        await self.send_json({
            "type": "bidders_count",
            "count": event["count"],
        })

    async def auction_ending_soon(self, event):
        await self.send_json({
            "type": "auction_ending_soon",
            "time_to_end": event["time_to_end"],
        })

    @database_sync_to_async
    def get_auction(self):
        return Auction.objects.get(id=self.auction_id)