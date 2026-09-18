from dataclasses import dataclass

@dataclass
class OutbidPayload:
    auction_id: str
    receiver_id: str
    listing_id: str
    listing_name: str
    bid_price: str

@dataclass
class OutbidDTO:
    event_type: str
    payload: OutbidPayload