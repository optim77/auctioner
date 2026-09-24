from uuid import UUID

from auction.models import Auction, AuctionStatus
from django.db import transaction
from django.utils import timezone

from events.ws.events import BidPlacedEvent
from events.kafka.events import KafkaBidOutbidEvent
from events.kafka.publisher import KafkaPublisher
from events.ws.publisher import EventPublisher
from rest_framework.exceptions import ValidationError

from bid.models import Bid
from users.models import User


class BidService:

    @staticmethod
    @transaction.atomic
    def place_bid(*, auction_id: UUID, bidder: User, bid_price: int) -> Bid:
        auction: Auction = (
            Auction.objects
            .select_for_update()
            .get(id=auction_id)
        )

        if auction.status != AuctionStatus.ACTIVE:
            raise ValidationError(
                "Auction is not active."
            )

        if auction.end_date <= timezone.now():
            raise ValidationError(
                "Auction has expired."
            )

        if auction.listing.seller_id == bidder.id:
            raise ValidationError(
                "Seller cannot bid on their own auction."
            )

        highest_bid = (
            Bid.objects
            .filter(auction=auction)
            .order_by("-bid_price")
            .first()
        )

        minimum_bid: int = (
            highest_bid.bid_price
            if highest_bid
            else auction.start_price
        )

        if bid_price <= minimum_bid:
            raise ValidationError(
                f"Bid must be greater than "
                f"{minimum_bid} {auction.currency}."
            )

        bid = Bid.objects.create(
            auction=auction,
            bidder=bidder,
            bid_price=bid_price,
        )

        auction.current_price = bid_price
        auction.save(update_fields=["current_price"])

        bid_placed_event = BidPlacedEvent(
            auction_id=auction.id,
            bid_id=bid.id,
            bidder_id=bid.bidder.id,
            bid_price=str(bid.bid_price),
            current_price=str(auction.current_price),
        )
        print(bid_placed_event)

        transaction.on_commit(
            lambda: EventPublisher.publish(bid_placed_event)
        )

        if highest_bid:
            outbid_event = KafkaBidOutbidEvent(
                auction_id=auction.id,
                bid_price=str(bid.bid_price),
                receiver_id=highest_bid.bidder.id,
                listing_id=auction.listing.id,
                listing_name=auction.listing.name,
            )

            transaction.on_commit(
                lambda event=outbid_event: KafkaPublisher.publish(event)
            )

        return bid