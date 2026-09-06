from celery import shared_task

from auction.services.services import AuctionServices


@shared_task
def expire_auctions_task():
    AuctionServices.expire_auctions()