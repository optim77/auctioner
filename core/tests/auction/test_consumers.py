import pytest
from asgiref.sync import sync_to_async
from django.utils import timezone

from auction.models import Auction, AuctionStatus
from auction.services.services import AuctionServices
from auction.tasks import check_auctions_ending_soon
from bid.realtime import publish_bid_placed
from bid.services.services import BidService
from channels.testing import WebsocketCommunicator
from core.asgi import application
from events.events import BidPlacedEvent


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_can_connect_to_auction_websocket(auction: Auction):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    connected, _ = await communicator.connect()

    assert connected is True

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_receives_bid_placed_event(auction, bidder):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    connected, _ = await communicator.connect()

    assert connected is True
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_state",
        "auction_id": str(auction.id),
        "status": auction.status,
        "current_price": '100.00',
        "end_date": auction.end_date.isoformat(),
    }
    bid = await sync_to_async(BidService.place_bid)(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=200,
    )
    response = await communicator.receive_json_from()
    assert response == {
        "type": "bid_placed",
        "auction_id": str(auction.id),
        "bid_id": str(bid.id),
        "bidder_id": str(bid.bidder.id),
        "bid_price": str(bid.bid_price),
        "current_price": "200",
    }

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_receives_auction_started_event(draft_auction):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{draft_auction.id}/",
    )

    connected, _ = await communicator.connect()
    assert connected is True
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_state",
        "auction_id": str(draft_auction.id),
        "status": draft_auction.status,
        "current_price": "100.00",
        "end_date": draft_auction.end_date.isoformat(),
    }
    auction = await sync_to_async(AuctionServices.activate)(auction_id=draft_auction.id)
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_started",
        "auction_id": str(auction.id),
        "status":  auction.status,
        "start_price": str(auction.start_price),
    }
    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_receives_auction_ended_event(auction):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction.id}/",
    )

    connected, _ = await communicator.connect()
    assert connected is True
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_state",
        "auction_id": str(auction.id),
        "status": auction.status,
        "current_price": "100.00",
        "end_date": auction.end_date.isoformat(),
    }
    auction = await sync_to_async(AuctionServices.close_auction)(auction_id=auction.id)
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_ended",
        "auction_id": str(auction.id),
        "status":  auction.status,
        "final_price": str(auction.final_price),
    }
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_client_receives_auction_ending_soon_event(auction_ending_soon):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/auctions/{auction_ending_soon.id}/",
    )

    connected, _ = await communicator.connect()
    assert connected is True
    response = await communicator.receive_json_from()
    assert response == {
        "type": "auction_state",
        "auction_id": str(auction_ending_soon.id),
        "status": auction_ending_soon.status,
        "current_price": "100.00",
        "end_date": auction_ending_soon.end_date.isoformat(),
    }
    await sync_to_async(check_auctions_ending_soon)()
    response = await communicator.receive_json_from()
    assert response["type"] == "auction_ending_soon"
    assert 0 <= int(response["time_to_end"]) <= 60
    await communicator.disconnect()
