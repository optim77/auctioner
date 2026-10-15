from auction.models import AuctionStatus as S


class InvalidAuctionTransition(Exception):
    pass

ALLOWED = {
    S.DRAFT:   {S.ACTIVE},
    S.ACTIVE:  {S.SOLD, S.EXPIRED},
    S.SOLD:    set(),
    S.EXPIRED: set(),
}


def ensure_transition(current: str, target: str):
    if target not in ALLOWED[current]:
        raise InvalidAuctionTransition(f"{current} -> {target}")

def ensure_active(status: str) -> None:
    if status != S.ACTIVE:
        raise InvalidAuctionTransition(f"Auction is not active ({status})")