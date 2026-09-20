from dataclasses import dataclass

@dataclass
class OutbidPayload:
    auction_id: str
    receiver_id: str
    listing_id: str
    listing_name: str
    bid_price: str

@dataclass(frozen=True)
class OutbidDTO:
    event_type: str
    payload: OutbidPayload

@dataclass
class AuctionStartedPayload:
    auction_id: str
    status: str
    start_price: str
    listing_id: str
    listing_name: str
    receiver_id: str

@dataclass(frozen=True)
class AuctionStartedDTO:
    event_type: str
    payload: AuctionStartedPayload
