from uuid import UUID

from auction.models import Auction
from auction.rules import ensure_active
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from events.kafka.events import KafkaBidOutbidEvent
from events.kafka.publisher import KafkaPublisher
from events.ws.events import BidPlacedEvent
from events.ws.publisher import EventPublisher
from rest_framework.exceptions import ValidationError
from users.models import User

from bid.models import Bid
from bid.selectors import get_highest_bid


class BidService:

    @staticmethod
    @transaction.atomic
    def place_bid(*, auction_id: UUID, bidder: User, bid_price: int) -> Bid:
        auction: Auction = (
            Auction.objects.select_for_update(of=("self",))
            .select_related("listing")
            .get(id=auction_id)
        )
        ensure_active(auction.status)

        if auction.end_date <= timezone.now():
            raise ValidationError("Auction has expired.")
        if auction.listing.seller_id == bidder.id:
            raise ValidationError("Seller cannot bid on their own auction.")

        highest_bid = get_highest_bid(auction)
        minimum_bid: int = highest_bid.bid_price if highest_bid else auction.start_price

        if bid_price <= minimum_bid:
            raise ValidationError(f"Bid must be greater than {minimum_bid} {auction.currency}.")
        if not bidder.is_active:
            raise ValidationError("Bidder is not active.")

        bid = Bid.objects.create(auction=auction, bidder=bidder, bid_price=bid_price)

        auction.current_price = bid_price
        # Atomic increment: the counter can never be lost even if another
        # writer updates it between our read and our write.
        Auction.objects.filter(id=auction.id).update(
            current_price=bid_price,
            bids_counter=F("bids_counter") + 1,
        )

        bid_placed_event = BidPlacedEvent(
            auction_id=auction.id,
            bid_id=bid.id,
            bid_price=str(bid.bid_price),
            current_price=str(auction.current_price),
        )

        transaction.on_commit(lambda: EventPublisher.publish(bid_placed_event))

        if highest_bid and highest_bid.bidder_id != bidder.id:
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