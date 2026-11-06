from rest_framework.exceptions import ValidationError

from auction.models import AuctionStatus

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    AuctionStatus.DRAFT: {AuctionStatus.ACTIVE},
    AuctionStatus.ACTIVE: {AuctionStatus.SOLD, AuctionStatus.EXPIRED},
    AuctionStatus.SOLD: set(),
    AuctionStatus.EXPIRED: set(),
}


class InvalidAuctionTransition(ValidationError):
    """Raised when an auction cannot move to the requested status."""

    default_detail = "Invalid auction transition."
    default_code = "invalid_transition"


def ensure_transition(current: str, target: str) -> None:
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidAuctionTransition(f"{current} -> {target}")


def ensure_active(status: str) -> None:
    if status != AuctionStatus.ACTIVE:
        raise InvalidAuctionTransition(f"Auction is not active ({status})")
