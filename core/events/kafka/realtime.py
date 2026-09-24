from wsgiref import headers

from core.kafka import producer
from events.kafka.events import (
    KafkaAuctionEndedEvent,
    KafkaAuctionStartedEvent,
    KafkaBidPlacedEvent,
    KafkaBidOutbidEvent
)

def publish_auction_started(event: KafkaAuctionStartedEvent):
    producer.send(
        "auction.started",
        value={
            "event_type": "auction.started",
            "payload": {
                "auction_id": str(event.auction_id),
                "status": event.status,
                "start_price": event.start_price,
                "listing_id": str(event.listing_id),
                "listing_name": event.listing_name,
                "receiver_id": str(event.receiver_id)
            }
        },
        headers=[("__TypeId__", b"startedEvent")]
    )


def publish_auction_ended(event: KafkaAuctionEndedEvent):
    producer.send(
        "auction.ended",
        value={
            "event_type": "auction.ended",
            "payload": {
                "auction_id": str(event.auction_id),
                "receiver_id": str(event.receiver_id),
                "listing_id": str(event.listing_id),
                "listing_name": event.listing_name,
                "final_price": event.final_price,
            },
        },
    )

def publish_bid_placed(event: KafkaBidPlacedEvent):
    producer.send(
        "bid.placed",
        value={
            "event_type": "bid.placed",
            "payload": {
                "auction_id": str(event.auction_id),
                "receiver_id": str(event.receiver_id),
                "listing_id": str(event.listing_id),
                "listing_name": event.listing_name,
                "bid_price": event.bid_price,
                "current_price": event.current_price
            },
        },
        headers=[("__TypeId__", b"placedEvent")]
    )

def publish_bid_outbid(event: KafkaBidOutbidEvent):
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
        headers=[("__TypeId__", b"outbidEvent")]
    )
