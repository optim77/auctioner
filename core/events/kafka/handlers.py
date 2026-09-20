from events.kafka.realtime import (
    publish_auction_ended,
    publish_auction_started,
    publish_bid_placed,
    publish_bid_outbid,
)

from events.kafka.events import (
    BidPlacedEvent,
    AuctionEndedEvent,
    AuctionStartedEvent,
    BidOutbidEvent,
)

def handle_bid_placed(event: BidPlacedEvent) -> None:
    publish_bid_placed(event)

def handle_auction_started(event: AuctionStartedEvent) -> None:
    publish_auction_started(event)

def handle_auction_ended(event: AuctionEndedEvent) -> None:
    publish_auction_ended(event)

def handle_bid_outbid(event: BidOutbidEvent) -> None:
    publish_bid_outbid(event)

KAFKA_EVENT_HANDLERS = {
    BidPlacedEvent: handle_bid_placed,
    AuctionEndedEvent: handle_auction_ended,
    AuctionStartedEvent: handle_auction_started,
    BidOutbidEvent: handle_bid_outbid
}