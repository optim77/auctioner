from celery import shared_task
from django.db import OperationalError, transaction
from django.db.models import Avg
from users.models import User

from rating.models import Rating


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def sum_user_rating():
    """Recompute the average rating of users flagged as changed.

    ``sum_user_rating`` on ``User`` acts as a dirty flag set when a new
    rating is created; after recomputation the flag is cleared.
    """
    flagged_ids = User.objects.filter(
        sum_user_rating=True, deleted=False
    ).values_list('id', flat=True)

    for user_id in flagged_ids:
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=user_id)
            if not user.sum_user_rating:
                continue

            average = Rating.objects.filter(rated_user=user).aggregate(
                value=Avg('rating')
            )['value']

            update_fields = ['sum_user_rating']
            if average is not None:
                user.rating = round(average)
                update_fields.append('rating')

            user.sum_user_rating = False
            user.save(update_fields=update_fields)
