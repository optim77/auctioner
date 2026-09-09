import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator

from auction.models import Auction
from bid.realtime import publish_bid_placed
from bid.services.bid_service import BidService
from core.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_client_can_connect_to_auction_websocket(auction: Auction):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    connected, _ = await communicator.connect()

    assert connected is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_client_receives_bid_placed_event(auction, bidder):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    connected, _ = await communicator.connect()

    assert connected is True

    await sync_to_async(BidService.place_bid)(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=200,
    )

    auction = await sync_to_async(
        type(auction).objects.get
    )(id=auction.id)

    await sync_to_async(publish_bid_placed)(auction)

    response = await communicator.receive_json_from()

    assert response == {
        "type": "bid_placed",
        "auction_id": str(auction.id),
        "current_price": "200",
    }

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_bid_placed_event_is_sent_only_to_correct_auction(
    auction,
    second_auction,
):
    communicator_1 = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    communicator_2 = WebsocketCommunicator(
        application,
        f"/ws/auctions/{second_auction.id}/",
    )

    connected_1, _ = await communicator_1.connect()
    connected_2, _ = await communicator_2.connect()

    assert connected_1 is True
    assert connected_2 is True

    auction.current_price = 200
    await sync_to_async(auction.save)(update_fields=["current_price"])

    await sync_to_async(publish_bid_placed)(auction)

    response = await communicator_1.receive_json_from()

    assert response == {
        "type": "bid_placed",
        "auction_id": str(auction.id),
        "current_price": "200",
    }

    with pytest.raises(Exception):
        await communicator_2.receive_json_from(timeout=0.2)

    await communicator_1.disconnect()
    await communicator_2.disconnect()