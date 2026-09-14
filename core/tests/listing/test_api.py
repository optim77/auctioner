import pytest

from categories.models import Category
from listing.models import Listing


@pytest.mark.django_db
def test_unauthorized_user_can_fetch_listings(
        api_client,
        listing,
):
    response = api_client.get(
        "/listing/",
        format="json",
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(listing.id)


@pytest.mark.django_db
def test_unauthorized_user_can_fetch_listing(
        api_client,
        listing,
):
    response = api_client.get(
        f"/listing/{listing.id}/",
        format="json",
    )
    assert response.status_code == 200
    assert response.data['id'] == str(listing.id)


@pytest.mark.django_db
def test_unauthorized_user_cant_create_listing(
        api_client,
        listing,
        seller,
        category
):
    response = api_client.post(
        f"/listing/",
        {
            "seller": seller.id,
            "name": "test",
            "description": "test",
            "category": category.id,
        },
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthorized_user_cant_update_listing(
        api_client,
        listing,
        seller,
        category
):
    response = api_client.patch(
        f"/listing/{listing.id}/",
        {
            "seller": seller.id,
            "name": "test2",
            "description": "test2",
            "category": category.id,
        },
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthorized_user_cant_delete_listing(
        api_client,
        listing,
        bidder,
        category
):
    response = api_client.delete(
        f"/listing/{listing.id}/",
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_authorized_user_can_fetch_listings(
        api_client,
        listing,
        seller
):
    api_client.force_authenticate(user=seller)
    response = api_client.get(
        "/listing/",
        format="json",
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(listing.id)


@pytest.mark.django_db
def test_authorized_user_can_fetch_listing(
        api_client,
        listing,
        seller
):
    api_client.force_authenticate(user=seller)
    response = api_client.get(
        f"/listing/{listing.id}/",
        format="json",
    )
    assert response.status_code == 200
    assert response.data['id'] == str(listing.id)


@pytest.mark.django_db
def test_other_user_cant_update_listing(
        api_client,
        listing,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.patch(
        f"/listing/{listing.id}/",
        {
            "name": "test2",
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_other_user_cant_delete_listing(
        api_client,
        listing,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.delete(
        f"/listing/{listing.id}/",
        {
            "name": "test2",
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_authorized_user_can_create_listing(
        api_client,
        seller,
        category
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        f"/listing/",
        {
            "seller": seller.id,
            "name": "test2",
            "description": "test2",
            "category": category.id,
        },
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_owner_user_can_update_listing(
        api_client,
        listing,
        seller
):
    api_client.force_authenticate(user=seller)
    response = api_client.patch(
        f"/listing/{listing.id}/",
        {
            "name": "test2",
        },
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_owner_user_can_delete_listing(
        api_client,
        listing,
        seller
):
    api_client.force_authenticate(user=seller)
    response = api_client.delete(
        f"/listing/{listing.id}/",
        format="json",
    )
    assert response.status_code == 204
    assert Listing.objects.filter(id=listing.id).count() == 0


def test_category_items_counter_count_up_after_adding_listing(
        api_client,
        seller,
        category
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        f"/listing/",
        {
            "seller": seller.id,
            "name": "test2",
            "description": "test2",
            "category": category.id,
        },
        format="json",
    )
    assert response.status_code == 201
    assert Category.objects.get(id=category.id).items_amount == 2


def test_category_items_counter_count_down_after_adding_listing(
        api_client,
        seller,
        category
):
    api_client.force_authenticate(user=seller)
    response = api_client.post(
        f"/listing/",
        {
            "seller": seller.id,
            "name": "test2",
            "description": "test2",
            "category": category.id,
        },
        format="json",
    )
    assert response.status_code == 201
    assert Category.objects.get(id=category.id).items_amount == 2
    second_response = api_client.delete(
        f"/listing/{response.data['id']}/",
        format="json",
    )
    assert second_response.status_code == 204
    assert Category.objects.get(id=category.id).items_amount == 1


@pytest.mark.django_db
def test_owner_user_can_change_listing_category(
        api_client,
        seller,
        listing,
        category,
        second_category
):
    api_client.force_authenticate(user=seller)

    response = api_client.patch(
        f"/listing/{listing.id}/",
        {
            "category": second_category.id,
        },
        format="json",
    )

    category.refresh_from_db()
    second_category.refresh_from_db()

    assert response.status_code == 200
    assert second_category.items_amount == 1
    assert category.items_amount == 0
