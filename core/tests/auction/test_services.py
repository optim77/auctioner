import pytest
from rest_framework.exceptions import ValidationError

from auction.models import AuctionStatus
from auction.services.services import AuctionServices


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
        assert auction.status == AuctionStatus.EXPIRED