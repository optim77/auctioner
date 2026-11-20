from datetime import timedelta

import pytest
from auction.models import AuctionStatus
from auction.services import AuctionService
from bid.services import BidService
from django.utils import timezone
from rest_framework.exceptions import ValidationError


@pytest.mark.django_db
def test_set_active_from_draft(draft_auction):
    auction = AuctionService.activate(draft_auction.id)
    assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_active_from_active(auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.activate(auction.id)
        assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_expired_from_draft(draft_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.expire(draft_auction.id)
        assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_set_finish_from_draft(draft_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.finish(draft_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_finish_from_active(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    _end_auction(auction)
    auction = AuctionService.finish(auction.id)
    assert auction.status == AuctionStatus.SOLD
    assert auction.winner_id == bidder.id


@pytest.mark.django_db
def test_cannot_finish_before_end_date(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    with pytest.raises(ValidationError):
        AuctionService.finish(auction.id)


@pytest.mark.django_db
def test_cannot_finish_without_bids(auction):
    _end_auction(auction)
    with pytest.raises(ValidationError):
        AuctionService.finish(auction.id)


@pytest.mark.django_db
def test_cannot_activate_before_start_date(draft_auction):
    draft_auction.start_date = timezone.now() + timedelta(hours=1)
    draft_auction.save(update_fields=["start_date"])

    with pytest.raises(ValidationError):
        AuctionService.activate(draft_auction.id)

@pytest.mark.django_db
def test_set_finish_from_finished(finished_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.finish(finished_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_finish_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.finish(expired_auction.id)
        assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_set_active_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.activate(expired_auction.id)
        assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_set_sold_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        auction = AuctionService.finish(expired_auction.id)
        assert auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_set_expired_from_expired(expired_auction):
    with pytest.raises(ValidationError):
        AuctionService.expire(expired_auction.id)

@pytest.mark.django_db
def test_close_expired_auction(expired_auction):
    with pytest.raises(ValidationError):
        AuctionService.close_auction(expired_auction.id)

@pytest.mark.django_db
def test_close_sold_auction(finished_auction):
    with pytest.raises(ValidationError):
        closed_auction = AuctionService.close_auction(finished_auction.id)
        assert closed_auction.status == AuctionStatus.SOLD

@pytest.mark.django_db
def test_close_draft_auction(draft_auction):
    with pytest.raises(ValidationError):
        closed_auction = AuctionService.close_auction(draft_auction.id)
        assert closed_auction.status == AuctionStatus.DRAFT

def _end_auction(auction):
    auction.end_date = timezone.now() - timedelta(minutes=1)
    auction.save(update_fields=["end_date"])

@pytest.mark.django_db
def test_close_active_auction_without_bids(auction):
    _end_auction(auction)
    closed_auction = AuctionService.close_auction(auction.id)
    assert closed_auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_close_active_auction_with_bid(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    _end_auction(auction)
    closed_auction = AuctionService.close_auction(auction.id)
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
    _end_auction(auction)
    closed_auction = AuctionService.close_auction(auction.id)
    assert closed_auction.status == AuctionStatus.SOLD
    assert closed_auction.bids.count() == 2
    assert closed_auction.final_price == 160