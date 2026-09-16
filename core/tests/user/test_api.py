import pytest

from users.models import User


@pytest.mark.django_db
def test_user_cant_register_with_too_short_password(
        api_client
):
    response = api_client.post(
        "/auth/register/",
        {
            "email": "test5@test.com",
            "password": "test"
        },
        format="json"
    )
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_cant_register_with_existing_mail(
        api_client,
        test_user
):
    response = api_client.post(
        "/auth/register/",
        {
            "email": "test@test.com",
            "password": "testtest12"
        },
        format="json"
    )
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_can_register_with_unique_email(
        api_client
):
    response = api_client.post(
        "/auth/register/",
        {
            "email": "test5@test.com",
            "password": "testtest12"
        },
        format="json"
    )
    assert response.status_code == 201

@pytest.mark.django_db
def test_user_password_hash_correctly(
        api_client
):
    response = api_client.post(
        "/auth/register/",
        {
            "email": "test5@test.com",
            "password": "testtest12"
        },
        format="json"
    )
    assert 'pbkdf2_sha256$1500000$' in User.objects.get(email="test5@test.com").password
    assert response.status_code == 201


def test_user_can_login_with_correct_credentials(
        api_client,
        test_user
):
    response = api_client.post(
        "/auth/login/",
        {
            "email": "test@test.com",
            "password": "test"
        },
        format="json"
    )
    assert response.status_code == 200

def test_user_cant_login_with_correct_email_and_wrong_password(
        api_client,
        test_user
):
    response = api_client.post(
        "/auth/login/",
        {
            "email": "test@test.com",
            "password": "test2"
        },
        format="json"
    )
    assert response.status_code == 400

def test_user_can_fetch_their_account(
        api_client,
        test_user
):
    api_client.force_authenticate(user=test_user)
    response = api_client.get(
        "/profile/",
        format="json"
    )
    assert response.status_code == 200
    assert response.data["email"] == "test@test.com"

def test_user_can_update_their_account(
        api_client,
        test_user
):
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(
        "/profile/",
        {
            "username": "test2",
        },
        format="json"
    )
    test_user.refresh_from_db()
    assert response.status_code == 200
    assert test_user.username == "test2"

def test_user_can_update_their_password_with_correct_hashing(
        api_client,
        test_user
):
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(
        "/profile/",
        {
            "password": "passwd123123",
        },
        format="json"
    )
    test_user.refresh_from_db()
    assert response.status_code == 200
    assert "pbkdf2_sha256$1500000$" in test_user.password

def test_user_cant_update_their_email(
        api_client,
        test_user
):
    api_client.force_authenticate(user=test_user)
    response = api_client.patch(
        "/profile/",
        {
            "email": "test5@test.com",
        },
        format="json"
    )
    assert response.status_code == 400

def test_user_cant_post_to_profile(
        api_client,
        test_user
):
    api_client.force_authenticate(user=test_user)
    response = api_client.post(
        "/profile/",
        {
            "username": "test",
        },
        format="json"
    )
    assert response.status_code == 405

def test_unauthenticated_user_cannot_search_users(
        api_client,
        test_user
):
    response = api_client.get(
        "/users/",
        {
            "username": "test"
        },
        format="json"
    )
    assert response.status_code == 401

def test_unauthenticated_user_cant_fetch_user(
        api_client,
        bidder
):
    response = api_client.get(
        f"/users/{bidder.id}/",
        format="json"
    )
    assert response.status_code == 401


def test_authenticated_user_can_list_users(
        api_client,
        test_user,
        bidder
):
    api_client.force_authenticate(user=test_user)
    response = api_client.get(
        "/users/",
        format="json"
    )
    assert response.data['count'] == 2
    assert response.status_code == 200

def test_authenticated_user_can_search_users(
        api_client,
        test_user,
        bidder
):
    api_client.force_authenticate(user=test_user)
    response = api_client.get(
        "/users/?search=bidder",
        format="json"
    )
    assert response.status_code == 200
    assert response.data["username"] == "bidder"

def test_authenticated_user_can_fetch_user(
        api_client,
        test_user,
        bidder
):
    api_client.force_authenticate(user=test_user)
    response = api_client.get(
        f"/users/{bidder.id}/",
        format="json"
    )
    assert response.status_code == 200
    assert response.data["username"] == "bidder"