from channels.generic.websocket import AsyncJsonWebsocketConsumer


class AuctionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.group_name = f"auction_{self.auction_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def price_changed(self, event):
        await self.send_json({
            "type": "price_changed",
            "auction_id": event["auction_id"],
            "current_price": event["current_price"],
        })