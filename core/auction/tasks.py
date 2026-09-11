from datetime import timedelta

from bid.models import Bid
from bid.realtime import publish_auction_ending_soon
from celery import chain, group, shared_task
from django.db import OperationalError, transaction
from django.utils import timezone
from utils.base_model import BaseModel

from auction.models import Auction, AuctionStatus
from auction.services.services import AuctionServices


class MailData(BaseModel):
    user_id: str
    email: str
    listing_id: str
    listing_name: str
    auction_id: str

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

    active = auctions.filter(
        status=AuctionStatus.ACTIVE
    ).count()

    sold = auctions.filter(
        status=AuctionStatus.SOLD
    ).count()

    expired = auctions.filter(
        status=AuctionStatus.EXPIRED
    ).count()

    total_bids = Bid.objects.count()

    print(f"active auctions: {active}")
    print(f"sold auctions: {sold}")
    print(f"expired auctions: {expired}")
    print(f"total bids: {total_bids}")

@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def check_auctions_ending_soon():
    now = timezone.now()
    soon = now + timedelta(minutes=5)

    auctions = Auction.objects.filter(
        status=AuctionStatus.ACTIVE,
        end_date__gt=now,
        end_date__lte=soon,
    )

    for auction in auctions:
        publish_auction_ending_soon(auction)
        print(
            f"Auction {auction.id} "
            f"ends at ({auction.end_date}) "
            f"current price ({auction.current_price}) "
        )

@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def get_data_for_mail(auction_id):
    auction = Auction.objects.get(id=auction_id)
    highest_bid = auction.bids.order_by("-bid_price").first()
    return MailData({
            "user_id": highest_bid.bidder.user_id,
            "email": highest_bid.bidder.email,
            "listing_id": auction.listing.listing_id,
            "listing_name": auction.listing.listing_name,
            "auction_id": auction.id,
        })

@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def send_payment_notification_mail(mail_data):
    # send_payment_mail(mail_data)
    # return mail_data["auction_id"]
    pass


@shared_task
def mark_auction_as_processed(auction_id):
    with transaction.atomic():
        auction = Auction.objects.select_for_update().get(id=auction_id)

        auction.processed = True
        auction.processing = False

        auction.save(update_fields=["processed", "processing"])

@shared_task
def reset_auction_processing(auction_id):
    Auction.objects.filter(
        id=auction_id,
        processed=False,
    ).update(
        processing=False,
    )

@shared_task
def process_sold_auctions():
    with transaction.atomic():
        auctions = list(
            Auction.objects
            .select_for_update(skip_locked=True)
            .filter(
                status=AuctionStatus.SOLD,
                processed=False,
                processing=False,
            )
        )

        auction_ids = [auction.id for auction in auctions]

        Auction.objects.filter(
            id__in=auction_ids
        ).update(
            processing=True
        )

    jobs = []

    for auction_id in auction_ids:
        jobs.append(
            chain(
                get_data_for_mail.s(auction_id),
                send_payment_notification_mail.s(),
                mark_auction_as_processed.s(),
            ).apply_async(link_error=reset_auction_processing.s(auction_id))
        )

    group(jobs).delay()



