from celery import shared_task
from django.db import OperationalError

from auction.services.services import AuctionServices


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def expire_auctions_task():
    AuctionServices.close_expired_auctions()