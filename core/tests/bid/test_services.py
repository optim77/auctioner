import threading

import pytest
from django.db import close_old_connections
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from auction.models import AuctionStatus
from bid.models import Bid
from bid.services.bid_service import BidService


@pytest.mark.django_db
def test_user_can_place_bid(auction, bidder):
    bid = BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=150,
    )

    assert bid.bidder == bidder
    assert bid.auction == auction
    assert bid.bid_price == 150

    auction.refresh_from_db()

    assert auction.current_price == 150

@pytest.mark.django_db
def test_bid_must_be_greater_than_current_price(auction, bidder):
    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=bidder,
            bid_price=99,
        )

@pytest.mark.django_db
def test_bid_cannot_be_equal_current_price(auction, bidder):
    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=bidder,
            bid_price=100,
        )

@pytest.mark.django_db
def test_seller_cannot_bid_own_auction(auction, seller):
    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=seller,
            bid_price=150,
        )

@pytest.mark.django_db
def test_cannot_bid_on_when_end_date_past(auction, bidder):
    auction.end_date = timezone.now() - timezone.timedelta(minutes=1)
    auction.save()
    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=bidder,
            bid_price=200,
        )

@pytest.mark.django_db
def test_cannot_bid_on_expired_auction(auction, bidder):
    auction.status = AuctionStatus.EXPIRED
    auction.save()
    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=bidder,
            bid_price=200,
        )

@pytest.mark.django_db
def test_current_price_update_after_bid(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=150,
    )

    auction.refresh_from_db()

    assert auction.current_price == 150

@pytest.mark.django_db
def test_bid_must_be_greater_than_previous_bid(auction, bidder):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=150,
    )

    with pytest.raises(ValidationError):
        BidService.place_bid(
            auction_id=auction.id,
            bidder=bidder,
            bid_price=140,
        )

@pytest.mark.django_db
def test_bid_is_saved(auction, bidder):
    bid = BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=150,
    )

    saved_bid = Bid.objects.get(id=bid.id)

    assert saved_bid.bidder == bidder
    assert saved_bid.auction == auction
    assert saved_bid.bid_price == 150

@pytest.mark.django_db
def test_history_of_bids(auction, bidder):
    first_bid = BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=150,
    )
    first_bid.save()

    second_bid = BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=170,
    )
    second_bid.save()

    third_bid = BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=190,
    )
    third_bid.save()

    assert Bid.objects.all().count() == 3
    assert Bid.objects.get(id=first_bid.id).bid_price == 150
    assert Bid.objects.get(id=second_bid.id).bid_price == 170
    assert Bid.objects.get(id=third_bid.id).bid_price == 190

@pytest.mark.django_db(transaction=True)
def test_two_bids_the_same_time(auction, bidder, second_bidder):
    barrier = threading.Barrier(2)
    results = []

    def place_bid(bidder):
        close_old_connections()

        try:
            barrier.wait()

            bid = BidService.place_bid(
                auction_id=auction.id,
                bidder=bidder,
                bid_price=170,
            )

            results.append(("success", bid.id))

        except ValidationError as exc:
            results.append(("error", str(exc)))

        finally:
            close_old_connections()

    thread_1 = threading.Thread(
        target=place_bid,
        args=(bidder,),
    )

    thread_2 = threading.Thread(
        target=place_bid,
        args=(second_bidder,),
    )

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()

    assert len(results) == 2

    assert sum(
        result[0] == "success"
        for result in results
    ) == 1

    assert sum(
        result[0] == "error"
        for result in results
    ) == 1

    assert Bid.objects.filter(
        auction=auction,
        bid_price=170,
    ).count() == 1