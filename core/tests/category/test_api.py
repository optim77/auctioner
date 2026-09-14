import pytest

from categories.models import Category


@pytest.mark.django_db
def test_unauthenticated_user_can_fetch_all_categories(
        api_client,
        category
):
    response = api_client.get(
        "/category/",
        format="json",
    )

    assert response.status_code == 200
    assert Category.objects.count() == 1


@pytest.mark.django_db
def test_unauthenticated_user_can_fetch_category(
        api_client,
        category
):
    response = api_client.get(
        f"/category/{category.id}/",
        format="json",
    )

    assert response.status_code == 200
    assert response.data["name"] == "test"


@pytest.mark.django_db
def test_unauthenticated_user_cant_create_category(
        api_client
):
    response = api_client.post(
        "/category/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cant_update_category(
        api_client,
        category
):
    response = api_client.patch(
        f"/category/{category.id}/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cant_delete_category(
        api_client,
        category
):
    response = api_client.delete(
        f"/category/{category.id}/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_can_fetch_all_categories(
        api_client,
        category,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.get(
        "/category/",
        format="json",
    )

    assert response.status_code == 200
    assert Category.objects.count() == 1

@pytest.mark.django_db
def test_authenticated_user_can_fetch_category(
        api_client,
        category,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.get(
        f"/category/{category.id}/",
        format="json",
    )

    assert response.status_code == 200
    assert response.data["name"] == "test"


@pytest.mark.django_db
def test_base_user_cant_create_category(
        api_client,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.post(
        "/category/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_base_user_cant_update_category(
        api_client,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.patch(
        "/category/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_base_user_cant_delete_category(
        api_client,
        bidder
):
    api_client.force_authenticate(user=bidder)
    response = api_client.delete(
        "/category/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_admin_user_can_create_category(
        api_client,
        admin
):
    api_client.force_authenticate(user=admin)
    response = api_client.post(
        "/category/",
        {
            "name": "test",
            "description": "test",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Category.objects.count() == 1

@pytest.mark.django_db
def test_admin_user_can_update_category(
        api_client,
        admin,
        category
):
    api_client.force_authenticate(user=admin)
    response = api_client.patch(
        f"/category/{category.id}/",
        {
            "name": "test2",
            "description": "test2",
        },
        format="json",
    )

    assert response.status_code == 200
    assert Category.objects.count() == 1
    assert Category.objects.get(name="test2").description == "test2"


@pytest.mark.django_db
def test_admin_user_can_update_category(
        api_client,
        admin,
        category
):
    api_client.force_authenticate(user=admin)
    response = api_client.delete(
        f"/category/{category.id}/",
        format="json",
    )

    assert response.status_code == 204
    assert Category.objects.count() == 0

