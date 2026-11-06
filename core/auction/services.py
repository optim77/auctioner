from datetime import timedelta
from uuid import UUID

from bid.selectors import get_highest_bid
from django.db import transaction
from django.utils import timezone
from events.kafka.events import KafkaAuctionEndedEvent, KafkaAuctionStartedEvent
from events.kafka.publisher import KafkaPublisher
from events.ws.events import (
    AuctionEndedEvent,
    AuctionEndingSoonEvent,
    AuctionStartedEvent,
)
from events.ws.publisher import EventPublisher

from auction.models import Auction, AuctionStatus
from auction.rules import InvalidAuctionTransition, ensure_transition
from auction.selectors import (
    get_auction_for_update,
    get_auctions_ending_between,
    get_bidder_ids,
    get_expired_auction_ids,
    get_watchlist_user_ids,
)


class AuctionServices:
    """Write-side operations for the auction lifecycle."""

    @staticmethod
    @transaction.atomic
    def activate(auction_id: UUID) -> Auction:
        auction = get_auction_for_update(auction_id)
        ensure_transition(auction.status, AuctionStatus.ACTIVE)

        auction.status = AuctionStatus.ACTIVE
        if auction.current_price is None:
            auction.current_price = auction.start_price
        auction.save(update_fields=["status", "current_price"])

        started_event = AuctionStartedEvent(
            auction_id=auction.id,
            status=auction.status,
            start_price=str(auction.start_price),
        )
        transaction.on_commit(lambda event=started_event: EventPublisher.publish(event))
        transaction.on_commit(lambda: AuctionServices.notify_watchers(auction))
        return auction

    @staticmethod
    @transaction.atomic
    def finish(auction_id: UUID) -> Auction:
        """Finish an active auction early and mark it as sold."""
        auction = get_auction_for_update(auction_id)
        ensure_transition(auction.status, AuctionStatus.SOLD)

        winning_bid = get_highest_bid(auction)
        AuctionServices._mark_as_sold(auction, winning_bid)
        return auction

    @staticmethod
    @transaction.atomic
    def expire(auction_id: UUID) -> Auction:
        auction = get_auction_for_update(auction_id)
        AuctionServices._mark_as_expired(auction, final_price=auction.start_price)
        return auction

    @staticmethod
    def close_expired_auctions() -> int:
        now = timezone.now()
        closed = 0

        for auction_id in get_expired_auction_ids(now):
            try:
                AuctionServices.close_auction(auction_id)
            except InvalidAuctionTransition:
                continue
            closed += 1

        return closed

    @staticmethod
    @transaction.atomic
    def close_auction(auction_id: UUID) -> Auction:
        """Close an auction once its end date has passed."""
        auction = get_auction_for_update(auction_id)
        winning_bid = get_highest_bid(auction)
        target_status = (
            AuctionStatus.SOLD if winning_bid is not None else AuctionStatus.EXPIRED
        )

        # Validate the transition even when the auction has not ended yet, so
        # already closed auctions are reported consistently.
        ensure_transition(auction.status, target_status)

        if auction.end_date > timezone.now():
            return auction

        if winning_bid is None:
            AuctionServices._mark_as_expired(auction, final_price=None)
        else:
            AuctionServices._mark_as_sold(auction, winning_bid)

        return auction

    @staticmethod
    def notify_ending_soon(
        *,
        now=None,
        soon=None,
    ) -> int:
        now = now or timezone.now()
        soon = soon or now + timedelta(minutes=5)
        auctions = get_auctions_ending_between(now, soon)

        notified = 0
        for auction in auctions:
            event = AuctionEndingSoonEvent(
                auction_id=auction.id,
                end_date=auction.end_date,
            )
            EventPublisher.publish(event)
            notified += 1

        return notified

    @staticmethod
    def notify_watchers(auction: Auction) -> None:
        if auction.status != AuctionStatus.ACTIVE:
            return

        for user_id in get_watchlist_user_ids(auction.id):
            event = KafkaAuctionStartedEvent(
                auction_id=auction.id,
                status=auction.status,
                start_price=str(auction.current_price),
                listing_name=auction.listing.name,
                listing_id=str(auction.listing_id),
                receiver_id=str(user_id),
            )
            KafkaPublisher.publish(event)

    @staticmethod
    def notify_bidders(auction: Auction) -> None:
        for user_id in get_bidder_ids(auction.id):
            event = KafkaAuctionEndedEvent(
                auction_id=auction.id,
                status=auction.status,
                final_price=(
                    str(auction.final_price)
                    if auction.final_price is not None
                    else None
                ),
                listing_name=auction.listing.name,
                listing_id=str(auction.listing_id),
                receiver_id=str(user_id),
            )
            KafkaPublisher.publish(event)

    @staticmethod
    def _mark_as_sold(auction: Auction, winning_bid) -> None:
        ensure_transition(auction.status, AuctionStatus.SOLD)

        auction.status = AuctionStatus.SOLD
        auction.sold_date = timezone.now()
        if winning_bid is not None:
            auction.winner = winning_bid.bidder
            auction.final_price = winning_bid.bid_price

        auction.save(
            update_fields=["status", "sold_date", "winner", "final_price"]
        )
        AuctionServices._publish_ended(auction)
        transaction.on_commit(lambda: AuctionServices.notify_bidders(auction))

    @staticmethod
    def _mark_as_expired(auction: Auction, *, final_price=None) -> None:
        ensure_transition(auction.status, AuctionStatus.EXPIRED)

        auction.status = AuctionStatus.EXPIRED
        auction.final_price = final_price
        auction.save(update_fields=["status", "final_price"])
        AuctionServices._publish_ended(auction)
        transaction.on_commit(lambda: AuctionServices.notify_bidders(auction))

    @staticmethod
    def _publish_ended(auction: Auction) -> None:
        event = AuctionEndedEvent(
            auction_id=auction.id,
            status=auction.status,
            final_price=(
                str(auction.final_price)
                if auction.final_price is not None
                else None
            ),
        )
        transaction.on_commit(lambda: EventPublisher.publish(event))
