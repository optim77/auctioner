from events.ws.realtime import (
    publish_auction_ended,
    publish_auction_ending_soon,
    publish_auction_started,
    publish_bid_placed,
)

from events.ws.events import (
    AuctionEndedEvent,
    AuctionEndingSoonEvent,
    AuctionStartedEvent,
    BidPlacedEvent,
)

def handle_bid_placed(event: BidPlacedEvent) -> None:
    publish_bid_placed(event)

def handle_auction_started(event: AuctionStartedEvent) -> None:
    publish_auction_started(event)

def handle_auction_ended(event: AuctionEndedEvent) -> None:
    publish_auction_ended(event)

def handle_auction_ending_soon(event : AuctionEndingSoonEvent) -> None:
    publish_auction_ending_soon(event)

WS_EVENT_HANDLERS  = {
    BidPlacedEvent: handle_bid_placed,
    AuctionEndedEvent: handle_auction_ended,
    AuctionStartedEvent: handle_auction_started,
    AuctionEndingSoonEvent: handle_auction_ending_soon,
}