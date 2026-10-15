from auction.models import Auction
from bid.models import Bid


def get_highest_bid(auction: Auction) -> Auction | None:
    return Bid.objects.filter(auction=auction).order_by("-bid_price").first()