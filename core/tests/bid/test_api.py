import pytest

from bid.models import Bid


@pytest.mark.django_db
def test_authenticated_user_can_place_bid(
    api_client,
    auction,
    bidder,
):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "150.00",
        },
        format="json",
    )

    assert response.status_code == 201

    bid = Bid.objects.get(
        auction=auction,
        bidder=bidder,
    )

    assert bid.bid_price == 150

@pytest.mark.django_db
def test_unauthenticated_user_cannot_place_bid(
    api_client,
    auction,
):
    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "150.00",
        },
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_bidder_is_taken_from_authenticated_user(
        api_client,
        auction,
        bidder,
        seller
):
    api_client.force_authenticate(user=bidder)
    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "150.00",
            "bidder": seller.id,
        },
        format="json",
    )

    assert response.status_code == 201
    bid = Bid.objects.get(
        auction=auction,
        bid_price=150,
    )

    assert bid.bidder == bidder

@pytest.mark.django_db
def test_cannot_place_bid_below_current_price(
    api_client,
    auction,
    bidder,
):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "99.00",
        },
        format="json",
    )

    assert response.status_code == 400

    assert not Bid.objects.filter(
        auction=auction,
        bidder=bidder,
    ).exists()

@pytest.mark.django_db
def test_cannot_place_bid_equal_to_current_price(
    api_client,
    auction,
    bidder,
):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "100.00",
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_seller_cannot_place_bid(
    api_client,
    auction,
    seller,
):
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "150.00",
        },
        format="json",
    )

    assert response.status_code == 400

from auction.models import AuctionStatus


@pytest.mark.django_db
def test_cannot_bid_on_inactive_auction(
    api_client,
    auction,
    bidder,
):
    auction.status = AuctionStatus.DRAFT
    auction.save(update_fields=["status"])

    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {
            "bid_price": "150.00",
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_bid_price_is_required(
    api_client,
    auction,
    bidder,
):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{auction.id}/bids/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert "bid_price" in response.data