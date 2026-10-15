import uuid

from auction.models import Auction
from django.db import models
from users.models import User


class Bid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, on_delete=models.PROTECT, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.PROTECT)
    bid_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["auction", "-bid_price"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(bid_price__gt=0), name="bid_price_positive"),
        ]
