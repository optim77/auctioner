from celery import shared_task
from django.db import OperationalError

from rating.models import Rating
from users.models import User


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def sum_user_rating():
     users = User.objects.filter(sum_user_rating=True, deleted=False)
     for user in users:
         ratings = Rating.objects.select_for_update().filter(rated_user=user)
         rate = 0
         for rating in ratings:
             rate += rating.rating
             user.rating = rate / ratings.count()
             user.sum_user_rating = False
             user.save(update_fields=['rating', 'sum_user_rating'])


