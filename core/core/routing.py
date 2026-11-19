from auction.consumers import AuctionConsumer
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from django.urls import path

from core.ws_auth import JWTAuthMiddleware

websocket_urlpatterns = [
    path(
        "ws/auctions/<uuid:auction_id>/",
        AuctionConsumer.as_asgi(),
    ),
]

websocket_application = AuthMiddlewareStack(
    JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
)
