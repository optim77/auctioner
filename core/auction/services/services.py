from django.db import transaction
from django.utils import timezone

from bid.models import Bid
from events.kafka.events import KafkaAuctionStartedEvent, KafkaAuctionEndedEvent
from events.kafka.publisher import KafkaPublisher
from events.ws.events import AuctionEndedEvent, AuctionStartedEvent
from events.ws.publisher import EventPublisher
from rest_framework.exceptions import ValidationError

from auction.models import Auction, AuctionStatus
from watchlist.models import Watchlist


class AuctionServices:

    @staticmethod
    @transaction.atomic
    def activate(auction_id) -> Auction:
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
        ws_event = AuctionStartedEvent(
            auction_id=auction_id,
            status=auction.status,
            start_price=str(auction.start_price),
        )

        transaction.on_commit(lambda: EventPublisher.publish(ws_event))
        transaction.on_commit(lambda: AuctionServices.notify_watchers(auction))
        return auction

    @staticmethod
    @transaction.atomic
    def finish(auction_id) -> Auction:
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
    def expire(auction_id) -> Auction:
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
    #TODO: These two methods need refactor but for now its good for testing duplication events


    @staticmethod
    @transaction.atomic
    def close_expired_auctions() -> None:
        auctions = Auction.objects.filter(
            status=AuctionStatus.ACTIVE,
            end_date__lte=timezone.now(),
        )

        for auction in auctions:
            closed_auction = AuctionServices.close_auction(auction.id)

            close_event = AuctionEndedEvent(
                auction_id=closed_auction.id,
                status=closed_auction.status,
                final_price=(
                    str(closed_auction.final_price)
                    if closed_auction.final_price is not None
                    else None
                ),
            )
            # handle_auction_ended
            transaction.on_commit(
                lambda event=close_event: EventPublisher.publish(event)
            )


    @staticmethod
    @transaction.atomic
    def close_auction(auction_id) -> Auction:
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
            auction.winner = winning_bid.bidder

        auction.save(
            update_fields=["status", "final_price"]
        )
        ended_event = AuctionEndedEvent(
            auction_id=auction.id,
            status=auction.status,
            final_price=str(auction.final_price),
        )
        transaction.on_commit(lambda event=ended_event: EventPublisher.publish(event))
        transaction.on_commit(lambda: AuctionServices.notify_bidders(auction))
        return auction

    @staticmethod
    def notify_watchers(auction: Auction) -> None:
        watchers = Watchlist.objects.filter(auction=auction.id)
        for watcher in watchers:
            if watcher.user.status == AuctionStatus.ACTIVE:
                kafka_event = KafkaAuctionStartedEvent(
                    auction_id=auction.id,
                    status=auction.status,
                    start_price=auction.current_price,
                    listing_name=auction.listing.name,
                    listing_id=auction.listing.id,
                    receiver_id=watcher.user.id

                )
                KafkaPublisher.publish(kafka_event)

    @staticmethod
    def notify_bidders(auction: Auction) -> None:
        bidders = Bid.objects.filter(auction_id=auction.id).order_by("-bid_price")
        for bidder in bidders:
            event = KafkaAuctionEndedEvent(
                auction_id=auction.id,
                status=auction.status,
                final_price=auction.final_price,
                listing_name=auction.listing.name,
                listing_id=auction.listing.id,
                receiver_id=bidder.id
            )
            KafkaPublisher.publish(event)