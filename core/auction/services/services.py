from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from auction.models import Auction, AuctionStatus
from events.events import AuctionEndedEvent, AuctionStartedEvent
from events.handler import EventPublisher


class AuctionServices:

    @staticmethod
    @transaction.atomic
    def activate(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.ACTIVE:
            raise ValidationError('Auction is already active')
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Cannot activate sold auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Cannot activate expired auction')
        auction.status = AuctionStatus.ACTIVE
        if auction.current_price is None:
            auction.current_price = auction.start_price

        auction.status = AuctionStatus.ACTIVE
        auction.save(update_fields=["status", "current_price"])
        started_event = AuctionStartedEvent(
            auction_id=auction_id,
            status=auction.status,
            start_price=str(auction.start_price),
        )
        transaction.on_commit(lambda: EventPublisher.publish(started_event))

    @staticmethod
    @transaction.atomic
    def finish(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.DRAFT:
            raise ValidationError('Cannot sell draft auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Cannot finish expired auction')
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Auction is already sold')
        auction.status = AuctionStatus.SOLD
        auction.save(update_fields=['status'])
        return auction

    @staticmethod
    @transaction.atomic
    def expire(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Cannot expire sold auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Auction is already expired')
        if auction.status == AuctionStatus.DRAFT:
            raise ValidationError('Cannot expire draft auction')
        auction.status = AuctionStatus.EXPIRED
        auction.save(update_fields=['status'])
        return auction

    @staticmethod
    @transaction.atomic
    def close_expired_auctions():
        auctions = Auction.objects.filter(
            status=AuctionStatus.ACTIVE,
            end_date__lte=timezone.now(),
        )

        for auction in auctions:
            closed_auction = AuctionServices.close_auction(auction.id)

            close_event = AuctionEndedEvent(
                auction_id=str(closed_auction.id),
                status=closed_auction.status,
                final_price=(
                    str(closed_auction.final_price)
                    if closed_auction.final_price is not None
                    else None
                ),
            )

            transaction.on_commit(
                lambda event=close_event: EventPublisher.publish(event)
            )


    @staticmethod
    @transaction.atomic
    def close_auction(auction_id):
        auction = (
            Auction.objects
            .select_for_update()
            .get(id=auction_id)
        )
        if auction.status != AuctionStatus.ACTIVE:
            raise ValidationError("Auction is already inactive")
        winning_bid = (
            auction.bids
            .order_by("-bid_price", "created_at")
            .first()
        )

        if winning_bid is None:
            auction.status = AuctionStatus.EXPIRED
        else:
            auction.status = AuctionStatus.SOLD
            auction.final_price = winning_bid.bid_price

        auction.save(
            update_fields=["status", "final_price"]
        )

        return auction