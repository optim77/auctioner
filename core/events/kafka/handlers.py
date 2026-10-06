from events.kafka.events import (
    KafkaAuctionEndedEvent,
    KafkaAuctionStartedEvent,
    KafkaBidOutbidEvent,
    KafkaBidPlacedEvent,
)
from events.kafka.realtime import (
    publish_auction_ended,
    publish_auction_started,
    publish_bid_outbid,
    publish_bid_placed,
)


def handle_bid_placed(event: KafkaBidPlacedEvent) -> None:
    publish_bid_placed(event)

def handle_auction_started(event: KafkaAuctionStartedEvent) -> None:
    publish_auction_started(event)

def handle_auction_ended(event: KafkaAuctionEndedEvent) -> None:
    publish_auction_ended(event)

def handle_bid_outbid(event: KafkaBidOutbidEvent) -> None:
    publish_bid_outbid(event)

KAFKA_EVENT_HANDLERS = {
    KafkaBidPlacedEvent: handle_bid_placed,
    KafkaAuctionEndedEvent: handle_auction_ended,
    KafkaAuctionStartedEvent: handle_auction_started,
    KafkaBidOutbidEvent: handle_bid_outbid
}