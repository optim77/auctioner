from unittest.mock import patch

import pytest
from celery.exceptions import Retry
from django.db import OperationalError
from django.utils import timezone

from auction.models import AuctionStatus
from auction.tasks import expire_auctions_task


@pytest.mark.django_db
def test_expire_auctions_task(auction):
    auction.end_date = timezone.now() - timezone.timedelta(minutes=1)
    auction.status = AuctionStatus.ACTIVE
    auction.save(update_fields=["end_date", "status"])

    expire_auctions_task()

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_expire_auctions_task_does_not_expire_active_auction(
    auction,
):
    auction.end_date = timezone.now() + timezone.timedelta(hours=1)
    auction.status = AuctionStatus.ACTIVE
    auction.save(update_fields=["end_date", "status"])

    expire_auctions_task()

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.ACTIVE

@pytest.mark.django_db
def test_expire_auctions_task_is_idempotent(auction):
    auction.end_date = timezone.now() - timezone.timedelta(minutes=1)
    auction.status = AuctionStatus.ACTIVE
    auction.save(update_fields=["end_date", "status"])

    expire_auctions_task()
    expire_auctions_task()

    auction.refresh_from_db()

    assert auction.status == AuctionStatus.EXPIRED

@pytest.mark.django_db
def test_expire_auctions_task_expires_multiple_auctions(
    auction,
    second_auction,
):
    now = timezone.now()

    for item in [auction, second_auction]:
        item.status = AuctionStatus.ACTIVE
        item.end_date = now - timezone.timedelta(minutes=1)
        item.save(update_fields=["status", "end_date"])

    expire_auctions_task()

    auction.refresh_from_db()
    second_auction.refresh_from_db()

    assert auction.status == AuctionStatus.EXPIRED
    assert second_auction.status == AuctionStatus.EXPIRED