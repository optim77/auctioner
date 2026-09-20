import pytest

from watchlist.models import Watchlist


@pytest.mark.django_db
def test_unauthenticated_user_cant_fetch_watchlist(api_client, watchlist):
    response = api_client.get(
        f"/watchlist/{watchlist.id}/",
        format="json",
    )
    assert response.status_code == 401

@pytest.mark.django_db
def test_unauthenticated_user_cant_create_watchlist(api_client, listing, test_user):
    response = api_client.post(
        "/watchlist/",
        {
            "listing": listing.id,
            "user": test_user.id,
        },
        format="json",
    )
    assert response.status_code == 401

@pytest.mark.django_db
def test_unauthenticated_user_cant_update_watchlist(api_client, listing, test_user):
    response = api_client.patch(
        "/watchlist/",
        {
            "notifications_enabled": True,
        },
        format="json",
    )
    assert response.status_code == 401

@pytest.mark.django_db
def test_unauthenticated_user_cant_delete_watchlist(api_client, listing, test_user):
    response = api_client.delete(
        "/watchlist/",
        {
            "notifications_enabled": True,
        },
        format="json",
    )
    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_cant_fetch_other_watchlist(api_client, watchlist, bidder):
    api_client.force_authenticate(bidder)
    response = api_client.get(
        f"/watchlist/{watchlist.id}/",
        format="json",
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_authenticated_user_cant_list_other_watchlist(api_client, bidder):
    api_client.force_authenticate(bidder)
    response = api_client.get(
        "/watchlist/",
        format="json",
    )
    assert response.status_code == 200
    assert response.data["count"] == 0

@pytest.mark.django_db
def test_authenticated_user_cant_update_other_watchlist(api_client, watchlist, bidder):
    api_client.force_authenticate(bidder)
    response = api_client.patch(
        f"/watchlist/{watchlist.id}/",
        {
            "notifications_enabled": True,
        },
        format="json",
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_authenticated_user_cant_delete_other_watchlist(api_client, watchlist, bidder):
    api_client.force_authenticate(bidder)
    response = api_client.delete(
        f"/watchlist/{watchlist.id}/",
        format="json",
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_authenticated_user_can_fetch_his_watchlist(api_client, watchlist, seller):
    api_client.force_authenticate(seller)
    response = api_client.get(
        f"/watchlist/{watchlist.id}/",
        format="json",
    )
    assert response.data['id'] is not None
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_list_his_watchlist(api_client, watchlist, seller):
    api_client.force_authenticate(seller)
    response = api_client.get(
        "/watchlist/",
        format="json",
    )
    assert response.data['count'] == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_create_watchlist(api_client, listing, seller):
    api_client.force_authenticate(seller)
    response = api_client.post(
        "/watchlist/",
        {
            "listing": listing.id,
            "user": seller.id,
        },
        format="json",
    )
    db_watchlist = Watchlist.objects.get(listing=listing.id, user=seller.id)
    assert db_watchlist is not None
    assert response.status_code == 201

@pytest.mark.django_db
def test_authenticated_user_can_update_watchlist(api_client, watchlist, seller):
    api_client.force_authenticate(seller)
    response = api_client.patch(
        f"/watchlist/{watchlist.id}/",
        {
            "notifications_enabled": False
        },
        format="json",
    )
    watchlist.refresh_from_db()
    assert response.status_code == 200
    assert watchlist.notifications_enabled == False


@pytest.mark.django_db
def test_authenticated_user_can_delete_watchlist(api_client, watchlist, seller):
    api_client.force_authenticate(seller)
    response = api_client.delete(
        f"/watchlist/{watchlist.id}/",
        format="json",
    )

    assert response.status_code == 204
    assert Watchlist.objects.filter(listing=watchlist.id, user=seller.id).count() == 0
