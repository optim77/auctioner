import pytest
from rating.tasks import sum_user_rating
from users.models import User


@pytest.mark.django_db
def test_sum_user_rating(rating, seller, auction, listing):
    sum_user_rating()

    db_seller = User.objects.get(id=seller.id)
    assert db_seller.rating == rating.rating


@pytest.mark.django_db
def test_sum_user_rating_resets_when_no_ratings_left(rating, seller):
    seller.rating = 5
    seller.save(update_fields=["rating"])

    rating.delete()
    sum_user_rating()

    db_seller = User.objects.get(id=seller.id)
    assert db_seller.rating == 0
    assert db_seller.sum_user_rating is False