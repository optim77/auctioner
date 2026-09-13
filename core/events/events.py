from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BidPlacedEvent:
    auction_id: str
    bid_id: str
    bidder_id: str
    bid_price: str
    current_price: str

@dataclass(frozen=True)
class AuctionStartedEvent:
    auction_id: str
    status: str
    start_price: str

@dataclass(frozen=True)
class AuctionEndedEvent:
    auction_id: str
    status: str
    final_price: str | None

@dataclass(frozen=True)
class AuctionEndingSoonEvent:
    auction_id: str
    end_date: datetime