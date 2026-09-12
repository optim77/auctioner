from bid.realtime import publish_bid_placed, publish_auction_ended, publish_auction_started, publish_auction_ending_soon
from events.events import BidPlacedEvent, AuctionEndedEvent, AuctionStartedEvent, AuctionEndingSoonEvent


def handle_bid_placed(event: BidPlacedEvent):
    publish_bid_placed(event)

def handle_auction_started(event: AuctionStartedEvent):
    publish_auction_started(event)

def handle_auction_ended(event: AuctionEndedEvent):
    publish_auction_ended(event)

def handle_auction_ending_soon(event : AuctionEndingSoonEvent):
    publish_auction_ending_soon(event)

class EventPublisher:
    @staticmethod
    def publish(event):
        handler = EVENT_HANDLERS.get(type(event))

        if handler is None:
            raise ValueError(
                f"No handler registered for {type(event).__name__}"
            )

        handler(event)


EVENT_HANDLERS = {
    BidPlacedEvent: handle_bid_placed,
    AuctionEndedEvent: handle_auction_ended,
}

