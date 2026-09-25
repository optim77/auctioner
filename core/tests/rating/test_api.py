import pytest

from rating.models import Rating


@pytest.mark.django_db
def test_unauthorized_user_can_fetch_rating(api_client, rating, finished_auction, seller):
    response = api_client.get(
        f"/rating/{seller.id}/",
        format="json",
    )
    assert response.data["results"][0]["rating"] == 5
    assert response.data["results"][0]["auction"] == finished_auction.id
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized_user_cant_update_rating(api_client, rating, finished_auction, seller):
    response = api_client.patch(
        f"/rating/{seller.id}/{rating.id}/",
        {
            "rating": 4,
        },
        format="json",
    )
    assert response.status_code == 403

@pytest.mark.django_db
def test_unauthorized_user_cant_delete_rating(api_client, rating, finished_auction, seller):
    response = api_client.delete(
        f"/rating/{seller.id}/{rating.id}/",
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_authorized_user_cant_modify_other_rating(api_client, rating, finished_auction, seller, test_user_2):
    api_client.force_authenticate(user=test_user_2)
    response = api_client.patch(
        f"/rating/{seller.id}/{rating.id}/",
        {
          "rating": 4,
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_authorized_user_can_add_rating_to_bought_item(api_client, finished_auction, seller, bidder, second_listing):
    api_client.force_authenticate(user=bidder)
    response = api_client.post(
        f"/rating/{seller.id}/",
        {
            "rating": 4,
            "rated_user": seller.id,
            "listing": second_listing.id,
            "auction": finished_auction.id,
            "opinion": "test",
        },
        format="json",
    )
    db_rate = Rating.objects.filter(author=bidder.id).first()
    assert db_rate.opinion == "test"
    assert response.status_code == 201

@pytest.mark.django_db
def test_authorized_user_can_patch_rating_to_bought_item(api_client, rating, bidder, seller):
    api_client.force_authenticate(user=bidder)
    response = api_client.patch(
        f"/rating/{seller.id}/{rating.id}/",
        {
            "opinion": "test test",
        },
        format="json",
    )
    db_rate = Rating.objects.filter(author=bidder.id).first()
    assert db_rate.opinion == "test test"
    assert response.status_code == 200

@pytest.mark.django_db
def test_authorized_user_can_delete_rating_to_bought_item(api_client, rating, test_user, seller, bidder):
    api_client.force_authenticate(user=bidder)
    response = api_client.delete(
        f"/rating/{seller.id}/{rating.id}/",
        format="json",
    )
    db_rate = Rating.objects.filter(author=bidder.id).first()
    assert db_rate is None
    assert response.status_code == 204

@pytest.mark.django_db
def test_authorized_user_cant_create_rating_to_not_bought_item(api_client, rating, test_user_2, seller, second_listing, finished_auction):
    api_client.force_authenticate(user=test_user_2)

    response = api_client.post(
        f"/rating/{seller.id}/",
        {
            "rating": 4,
            "rated_user": seller.id,
            "listing": second_listing.id,
            "auction": finished_auction.id,
            "opinion": "test",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_authorized_user_can_modify_own_rating(api_client, rating, finished_auction, seller, bidder):
    api_client.force_authenticate(user=bidder)
    response = api_client.patch(
        f"/rating/{seller.id}/{rating.id}/",
        {
          "rating": 4,
        },
        format="json",
    )
    rating.refresh_from_db()
    assert rating.rating == 4
    assert response.status_code == 200
