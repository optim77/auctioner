import json

from celery import shared_task
from django.db import OperationalError

from auction.models import Auction, AuctionStatus
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


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)

def do_log_analytics():
    auctions = Auction.objects.all()
    active = auctions.filter(status=AuctionStatus.ACTIVE).count()
    sold = auctions.filter(status=AuctionStatus.SOLD).count()
    inactive = auctions.filter(status=AuctionStatus.EXPIRED).count()
    print(f"active: {active}")
    print(f"inactive: {sold}")
    print(f"inactive: {inactive}")
