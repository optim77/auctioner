from core.kafka import producer
from events.events import (
    AuctionEndedEvent,
    AuctionStartedEvent,
    BidPlacedEvent,
)
from events.kafka.events import BidOutbidEvent


def publish_auction_started(event: AuctionStartedEvent):
    pass


def publish_auction_ended(event: AuctionEndedEvent):
    pass

def publish_bid_placed(event: BidPlacedEvent):
    pass

def publish_bid_outbid(event: BidOutbidEvent):
    producer.send(
        "bid.outbid",
        value={
            "event_type": "bid.outbid",
            "payload": {
                "auction_id": str(event.auction_id),
                "receiver_id": str(event.receiver_id),
                "listing_id": str(event.listing_id),
                "listing_name": event.listing_name,
                "bid_price": event.bid_price,
            },
        },
    )
