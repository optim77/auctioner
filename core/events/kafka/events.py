from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class BaseEvent(ABC):
    auction_id: UUID

@dataclass(frozen=True)
class BidPlacedEvent(BaseEvent):
    bid_id: UUID
    bidder_id: UUID
    bid_price: str
    current_price: str

@dataclass(frozen=True)
class AuctionStartedEvent(BaseEvent):
    status: str
    start_price: str
    listing_name: Optional[str] | None

@dataclass(frozen=True)
class AuctionEndedEvent(BaseEvent):
    status: str
    final_price: str | None

@dataclass(frozen=True)
class AuctionEndingSoonEvent(BaseEvent):
    end_date: datetime

@dataclass(frozen=True)
class BidOutbidEvent(BaseEvent):
    bid_price: str
    receiver_id: UUID
    listing_id: UUID
    listing_name: str | None