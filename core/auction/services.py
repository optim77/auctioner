from uuid import UUID

from auction.rules import ensure_transition, InvalidAuctionTransition
from bid.models import Bid
from django.db import transaction
from django.utils import timezone
from events.kafka.events import KafkaAuctionEndedEvent, KafkaAuctionStartedEvent
from events.kafka.publisher import KafkaPublisher
from events.ws.events import AuctionEndedEvent, AuctionStartedEvent
from events.ws.publisher import EventPublisher
from watchlist.models import Watchlist

from auction.models import Auction, AuctionStatus


class AuctionServices:

    @staticmethod
    @transaction.atomic
    def activate(auction_id: UUID) -> Auction:
        auction = Auction.objects.select_for_update().get(id=auction_id)
        ensure_transition(auction.status, AuctionStatus.ACTIVE)
        auction.status = AuctionStatus.ACTIVE
        auction.save(update_fields=["status", "current_price"])
        if auction.current_price is None:
            auction.current_price = auction.start_price

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
        highest_bid = (Bid.objects.filter(auction=auction).order_by("-bid_price", "created_at").first())
        ensure_transition(auction.status, AuctionStatus.SOLD)
        auction.status = AuctionStatus.SOLD
        auction.winner = auction.highest_bid.bidder
        auction.final_price = highest_bid.bid_price
        auction.save(update_fields=['status', 'winner', 'final_price'])
        return auction

    @staticmethod
    @transaction.atomic
    def expire(auction_id) -> Auction:
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        ensure_transition(auction.status, AuctionStatus.EXPIRED)
        auction.status = AuctionStatus.EXPIRED
        auction.final_price = auction.start_price
        auction.save(update_fields=['status', 'final_price'])
        return auction


    @staticmethod
    def close_expired_auctions() -> int:
        ids = list(
            Auction.objects.filter(status=AuctionStatus.ACTIVE, end_date__lte=timezone.now())
            .values_list("id", flat=True)
        )
        closed = 0
        for auction_id in ids:
            try:
                AuctionServices.close_auction(auction_id=auction_id)
                closed += 1
            except InvalidAuctionTransition:
                continue
        return closed


    @staticmethod
    @transaction.atomic
    def close_auction(auction_id) -> Auction:
        auction = (
            Auction.objects
            .select_for_update()
            .get(id=auction_id)
        )
        winning_bid = (
            auction.bids
            .order_by("-bid_price", "created_at")
            .first()
        )

        if winning_bid is None:
            ensure_transition(auction.status, AuctionStatus.EXPIRED)
            auction.status = AuctionStatus.EXPIRED
        else:
            ensure_transition(auction.status, AuctionStatus.SOLD)
            auction.status = AuctionStatus.SOLD
            auction.final_price = winning_bid.bid_price
            auction.winner = winning_bid.bidder
            auction.sold_date = timezone.now()

        auction.save(
            update_fields=["status", "final_price", "winner", "sold_date"]
        )
        ended_event = AuctionEndedEvent(
            auction_id=auction.id,
            status=auction.status,
            final_price=str(auction.final_price) if auction.final_price is not None else None,
        )
        transaction.on_commit(lambda event=ended_event: EventPublisher.publish(event))
        transaction.on_commit(lambda: AuctionServices.notify_bidders(auction))
        return auction

    @staticmethod
    def notify_watchers(auction: Auction) -> None:
        watchers = Watchlist.objects.filter(auction=auction.id)
        for watcher in watchers:
            if watcher.auction.status == AuctionStatus.ACTIVE:
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
        user_ids = Bid.objects.filter(auction_id=auction.id).values_list("bidder_id", flat=True).distinct()
        for user_id in user_ids:
            event = KafkaAuctionEndedEvent(
                auction_id=auction.id,
                status=auction.status,
                final_price=auction.final_price,
                listing_name=auction.listing.name,
                listing_id=auction.listing.id,
                receiver_id=user_id
            )
            KafkaPublisher.publish(event)