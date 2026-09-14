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


def test_user_can_update_their_account(
        api_client,
        test_user
):
    raise NotImplementedError()

def test_user_can_delete_their_account(
        api_client,
        test_user
):
    raise NotImplementedError()