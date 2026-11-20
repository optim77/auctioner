import logging

from core.kafka import get_kafka_producer

from events.kafka.events import (
    KafkaAuctionEndedEvent,
    KafkaAuctionStartedEvent,
    KafkaBidOutbidEvent,
    KafkaBidPlacedEvent,
)

logger = logging.getLogger(__name__)

def _on_delivery_error(error, topic: str) -> None:
    logger.error("Kafka delivery to %s failed: %s", topic, error)


def _send(topic: str, value: dict, headers=None) -> None:
    """Queue a message without blocking the caller.

    Waiting for a broker acknowledgement (``future.get``) inside a request or
    a transaction callback added up to 10s of latency per recipient. The
    producer batches and retries internally; delivery errors are logged via a
    callback and never break the business transaction.
    """
    producer = get_kafka_producer()
    try:
        future = producer.send(topic, value=value, headers=headers)
        future.add_errback(_on_delivery_error, topic)
    except Exception:
        logger.exception("Kafka publish to %s failed", topic)


def publish_auction_started(event: KafkaAuctionStartedEvent) -> None:
    _send(
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


def publish_auction_ended(event: KafkaAuctionEndedEvent) -> None:
    _send(
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


def publish_bid_placed(event: KafkaBidPlacedEvent) -> None:
    _send(
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


def publish_bid_outbid(event: KafkaBidOutbidEvent) -> None:
    _send(
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
