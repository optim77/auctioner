from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class BaseEvent(ABC):
    auction_id: UUID

@dataclass(frozen=True)
class KafkaBidPlacedEvent(BaseEvent):
    bid_id: UUID
    bid_price: str
    current_price: str
    receiver_id: str
    listing_id: str
    listing_name: str

@dataclass(frozen=True)
class KafkaAuctionStartedEvent(BaseEvent):
    status: str
    start_price: str
    listing_name: Optional[str] | None
    listing_id: str
    receiver_id: str

@dataclass(frozen=True)
class KafkaAuctionEndedEvent(BaseEvent):
    status: str
    receiver_id: str
    listing_id: str
    listing_name: str | None
    final_price: str | None

@dataclass(frozen=True)
class KafkaAuctionEndingSoonEvent(BaseEvent):
    end_date: datetime

@dataclass(frozen=True)
class KafkaBidOutbidEvent(BaseEvent):
    bid_price: str
    receiver_id: str
    listing_id: str
    listing_name: str | None