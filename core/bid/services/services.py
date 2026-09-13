from auction.models import Auction, AuctionStatus
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from bid.models import Bid
from events.events import BidPlacedEvent
from events.handler import EventPublisher


class BidService:

    @staticmethod
    @transaction.atomic
    def place_bid(*, auction_id, bidder, bid_price):
        auction = (
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

        minimum_bid = (
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

        event = BidPlacedEvent(
            auction_id=str(auction.id),
            bid_id=str(bid.id),
            bidder_id=str(bid.bidder.id),
            bid_price=str(bid.bid_price),
            current_price=str(auction.current_price),
        )

        transaction.on_commit(
            lambda: EventPublisher.publish(event)
        )

        return bid