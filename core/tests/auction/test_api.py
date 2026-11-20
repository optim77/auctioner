from datetime import timedelta

import pytest
from auction.models import Auction, AuctionStatus
from auction.rules import InvalidAuctionTransition, ensure_transition
from auction.services import AuctionService
from bid.services import BidService
from django.utils import timezone


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_auction(
    api_client,
    listing,
):
    response = api_client.post(
        "/auctions/",
        {
            "start_price": 150,
            "listing": str(listing.id),
        },
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_unauthenticated_user_can_fetch_auctions(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )
    api_client.logout()
    get_response = api_client.get(
        f"/auctions/{response.data['id']}/",
        format="json",
    )

    assert get_response.status_code == 200

@pytest.mark.django_db
def test_unauthenticated_user_can_fetch_auction(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )
    api_client.logout()
    get_response = api_client.get(
        f"/auctions/{response.data['id']}/",
        format="json",
    )

    assert get_response.status_code == 200

@pytest.mark.django_db
def test_authenticated_user_can_create_auction(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price


@pytest.mark.django_db
def test_authenticated_user_can_update_auction(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price
    patch_response = api_client.patch(
        f"/auctions/{response.data['id']}/",
        {
            "start_price": "200.00",
        },
        format="json",
    )
    assert patch_response.data["start_price"] == "200.00"
    assert patch_response.status_code == 200

@pytest.mark.django_db
def test_authenticated_user_cannot_update_auction_status(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price
    patch_response = api_client.patch(
        f"/auctions/{response.data['id']}/",
        {
            "status": AuctionStatus.SOLD,
        },
        format="json",
    )
    assert patch_response.data["status"] != AuctionStatus.SOLD
    assert patch_response.status_code == 200

@pytest.mark.django_db
def test_authenticated_user_can_delete_auction(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price
    path_response = api_client.delete(
        f"/auctions/{response.data['id']}/",
        format="json",
    )
    assert path_response.status_code == 204
    assert not Auction.objects.filter(
        id=response.data["id"]
    ).exists()

@pytest.mark.django_db
def test_other_user_cannot_update_auction(
    api_client,
    bidder,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price

    api_client.force_authenticate(user=bidder)

    path_response = api_client.patch(
        f"/auctions/{response.data['id']}/",
        {
            "start_price": "200.00",
        },
        format="json",
    )
    assert path_response.status_code == 403

@pytest.mark.django_db
def test_other_user_cannot_delete_auction(
    api_client,
    bidder,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["status"] == AuctionStatus.DRAFT
    assert response.data["current_price"] == start_price

    api_client.force_authenticate(user=bidder)

    put_response = api_client.delete(
        f"/auctions/{response.data['id']}/",
        format="json",
    )
    assert put_response.status_code == 403


def test_other_user_cannot_create_auction_for_listing(
    api_client,
    bidder,
    listing,
):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )

    assert response.status_code == 403

def test_cannot_create_second_auction_for_listing(
    api_client,
    seller,
    listing,
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )
    assert response.status_code == 201

    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": str(listing.id),
            "currency": "PLN",
        },
        format="json",
    )
    assert Auction.objects.all().count() == 1
    assert response.status_code == 400

@pytest.mark.django_db
def test_active_auction_is_expired_after_end_date(
    auction,
):
    auction.end_date = timezone.now() - timedelta(minutes=1)
    auction.save(update_fields=["end_date"])

    AuctionService.close_auction(auction.id)

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_active_auction_is_not_expired_before_end_date(
    auction,
):
    auction.end_date = timezone.now() + timedelta(hours=1)
    auction.save(update_fields=["end_date"])

    AuctionService.close_auction(auction.id)

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.ACTIVE


@pytest.mark.django_db
def test_fetch_newest_auction(api_client, auction, auction_ending_soon):
    response = api_client.get(
        '/newest_auctions/',
        format="json",
    )

    assert response.data['count'] == 2
    assert response.status_code == 200

def test_newest_in_category(api_client, listing, category):
    response = api_client.get(
        f'/newest_category_auctions/{category.name}/',
        format="json",
    )

    print(response.data)
    assert response.status_code == 200

def test_hot_auction(api_client, listing, auction, auction_ending_soon):
    response = api_client.get(
        '/hot_auctions/',
        format="json",
    )

    print(response.data)
    assert response.data['count'] == 2
    assert response.status_code == 200


def test_active_auction_can_be_sold():
    ensure_transition(AuctionStatus.ACTIVE, AuctionStatus.SOLD)

def test_sold_auction_cannot_be_activated():
    with pytest.raises(InvalidAuctionTransition):
        ensure_transition(AuctionStatus.SOLD, AuctionStatus.ACTIVE)


@pytest.mark.django_db
def test_seller_can_activate_draft_auction(api_client, seller, draft_auction):
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        f"/auctions/{draft_auction.id}/activate/",
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == AuctionStatus.ACTIVE


@pytest.mark.django_db
def test_other_user_cannot_activate_auction(api_client, bidder, draft_auction):
    api_client.force_authenticate(user=bidder)

    response = api_client.post(
        f"/auctions/{draft_auction.id}/activate/",
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_seller_cannot_finish_auction_before_end_date(api_client, seller, auction):
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        f"/auctions/{auction.id}/finish/",
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_seller_can_finish_ended_auction_with_bid(
    api_client, seller, auction, bidder
):
    BidService.place_bid(
        auction_id=auction.id,
        bidder=bidder,
        bid_price=120,
    )
    auction.end_date = timezone.now() - timedelta(minutes=1)
    auction.save(update_fields=["end_date"])
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        f"/auctions/{auction.id}/finish/",
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == AuctionStatus.SOLD
    assert response.data["winner"] == bidder.id


@pytest.mark.django_db
def test_seller_cannot_change_auction_listing(
    api_client, seller, draft_auction, second_listing
):
    api_client.force_authenticate(user=seller)

    response = api_client.patch(
        f"/auctions/{draft_auction.id}/",
        {"listing": str(second_listing.id)},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_cannot_change_price_or_dates_of_active_auction(
    api_client, seller, auction
):
    api_client.force_authenticate(user=seller)

    price_response = api_client.patch(
        f"/auctions/{auction.id}/",
        {"start_price": "200.00"},
        format="json",
    )
    date_response = api_client.patch(
        f"/auctions/{auction.id}/",
        {"end_date": timezone.now() + timedelta(days=30)},
        format="json",
    )

    assert price_response.status_code == 400
    assert date_response.status_code == 400


@pytest.mark.django_db
def test_create_auction_with_malformed_listing_id_returns_400(
    api_client, seller
):
    api_client.force_authenticate(user=seller)

    response = api_client.post(
        "/auctions/",
        {
            "start_price": "120.00",
            "start_date": timezone.now(),
            "end_date": timezone.now() + timedelta(days=7),
            "listing": "not-a-uuid",
        },
        format="json",
    )

    assert response.status_code == 403