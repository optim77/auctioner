from auction.consumers import AuctionConsumer
from django.urls import path

websocket_urlpatterns = [
    path(
        "ws/auctions/<uuid:auction_id>/",
        AuctionConsumer.as_asgi(),
    ),
]