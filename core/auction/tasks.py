from attr import asdict
from celery import chain, group, shared_task
from django.db import OperationalError, transaction
from mail_service.sender import MailData, send_payment_mail
from utils.redis_client import redis_client

from auction.models import Auction
from auction.selectors import get_auction, get_sold_auctions_to_process
from auction.services import AuctionServices


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def expire_auctions_task() -> None:
    AuctionServices.close_expired_auctions()


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def do_log_analytics() -> None:
    pass


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def check_auctions_ending_soon() -> None:
    AuctionServices.notify_ending_soon()


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def get_data_for_mail(auction_id) -> dict:
    auction = get_auction(auction_id)

    if auction.winner is None:
        raise ValueError(f"Auction {auction_id} has no winner.")

    return asdict(
        MailData(
            user_id=str(auction.winner_id),
            email=auction.winner.email,
            listing_id=str(auction.listing_id),
            listing_name=auction.listing.name,
            auction_id=str(auction.id),
        )
    )


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
    acks_late=True,
    retry_jitter=True,
)
def send_payment_notification_mail(mail_data: dict) -> str:
    idempotency_key = (
        f"payment-mail:{mail_data['auction_id']}:{mail_data['user_id']}"
    )
    was_added = redis_client.set(idempotency_key, "processing", nx=True, ex=3600)
    if not was_added:
        return mail_data["auction_id"]

    send_payment_mail(MailData(**mail_data))
    return mail_data["auction_id"]


@shared_task
def mark_auction_as_processed(auction_id) -> None:
    with transaction.atomic():
        auction = Auction.objects.select_for_update().get(id=auction_id)
        auction.processed = True
        auction.processing = False
        auction.save(update_fields=["processed", "processing"])


@shared_task
def reset_auction_processing(auction_id, *_args, **_kwargs) -> None:
    Auction.objects.filter(
        id=auction_id,
        processed=False,
    ).update(
        processing=False,
    )


@shared_task
def process_sold_auctions() -> None:
    with transaction.atomic():
        auctions = list(
            get_sold_auctions_to_process().select_for_update(skip_locked=True)
        )
        auction_ids = [auction.id for auction in auctions]

        Auction.objects.filter(id__in=auction_ids).update(processing=True)

    jobs = [
        chain(
            get_data_for_mail.s(auction_id),
            send_payment_notification_mail.s(),
            mark_auction_as_processed.s(),
        ).set(link_error=[reset_auction_processing.si(auction_id)])
        for auction_id in auction_ids
    ]

    if jobs:
        group(*jobs).apply_async()
