import pytest
from rest_framework.exceptions import ValidationError

from auction.models import AuctionStatus
from auction.services.services import AuctionServices
from bid.services.bid_service import BidService


@pytest.mark.django_db
def test_set_active_from_draft(draft_auction):
    auction = AuctionServices.activate(draft_auction.id)
    assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_active_from_active(auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.activate(auction.id)
        assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_expired_from_draft(draft_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.expire(draft_auction.id)
        assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_set_finish_from_draft(draft_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.finish(draft_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_finish_from_active(auction):
    auction = AuctionServices.finish(auction.id)
    assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_finish_from_finished(finished_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.finish(finished_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_finish_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.finish(expired_auction.id)
        assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_set_active_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.activate(expired_auction.id)
        assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_sold_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.finish(expired_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_expired_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionServices.expire(expired_auction.id)

@pytest.mark.django_db
def test_close_expired_auction(expired_auction):
    with pytest.raises(ValidationError):
        closed_auction = AuctionServices.close_auction(expired_auction.id)

@pytest.mark.django_db
def test_close_sold_auction(finished_auction):
    with pytest.raises(ValidationError):
        closed_auction = AuctionServices.close_auction(finished_auction.id)
        assert closed_auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_close_draft_auction(draft_auction):
    with pytest.raises(ValidationError):
        closed_auction = AuctionServices.close_auction(draft_auction.id)
        assert closed_auction.status == AuctionStatus.DRAFT

@pytest.mark.django_db
def test_close_active_auction_without_bids(auction):
    closed_auction = AuctionServices.close_auction(auction.id)
    assert closed_auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_close_active_auction_with_bid(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    closed_auction = AuctionServices.close_auction(auction.id)
    assert closed_auction.status == AuctionStatus.SOLD
    assert closed_auction.bids.count() == 1

@pytest.mark.django_db
def test_close_active_auction_with_bids(auction, bidder, second_bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    BidService.place_bid(
        auction_id=auction.id,
        bidder=second_bidder,
        bid_price=160,
    )
    closed_auction = AuctionServices.close_auction(auction.id)
    assert closed_auction.status == AuctionStatus.SOLD
    assert closed_auction.bids.count() == 2
    assert closed_auction.final_price == 160