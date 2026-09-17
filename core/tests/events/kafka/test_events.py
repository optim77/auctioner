import pytest

from bid.services.services import BidService


@pytest.mark.django_db
def test_create_outbid_event(
        api_client,
        listing,
        bidder,
        test_user,
        auction
):
    api_client.force_authenticate(test_user)
    BidService.place_bid(auction_id=auction.id, bidder=bidder, bid_price=200)
    BidService.place_bid(auction_id=auction.id, bidder=test_user, bid_price=300)

