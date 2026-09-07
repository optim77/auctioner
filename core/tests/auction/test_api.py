import pytest
from django.utils import timezone

from auction.models import AuctionStatus, Auction
from auction.services.services import AuctionServices


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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
    bidder,
    listing,
):
    api_client.force_authenticate(user=bidder)

    start_price = "120.00"

    response = api_client.post(
        "/auctions/",
        {
            "start_price": start_price,
            "start_date": timezone.now(),
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
            "end_date": timezone.now() + timezone.timedelta(days=7),
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
    auction.end_date = timezone.now() - timezone.timedelta(minutes=1)
    auction.save(update_fields=["end_date"])

    AuctionServices.close_expired_auctions()

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_active_auction_is_not_expired_before_end_date(
    auction,
):
    auction.end_date = timezone.now() + timezone.timedelta(hours=1)
    auction.save(update_fields=["end_date"])

    AuctionServices.close_expired_auctions()

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.ACTIVE