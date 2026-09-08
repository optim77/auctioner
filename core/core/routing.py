from django.urls import path

from auction.consumers import AuctionConsumer


websocket_urlpatterns = [
    path(
        "ws/auctions/<uuid:auction_id>/",
        AuctionConsumer.as_asgi(),
    ),
]