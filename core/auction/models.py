import uuid
from typing import Self

from django.db.models import Q, QuerySet

from bid.utils.currencies import Currency
from django.db import models
from listing.models import Listing
from users.models import User

class AuctionQuerySet(models.QuerySet):
    def is_active(self) -> Self:
        return self.filter(status=AuctionStatus.ACTIVE)

    def search(self, query: str) -> Self:
        lookup = Q(listing__name__icontains=query) | Q(listing__description__icontains=query)
        return self.filter(lookup).is_active()

    def newest_auction(self) -> Self:
        return self.is_active().order_by("-created_at")[:10]

    def newest_auction_in_category(self, category: str) -> Self:
        lookup = Q(listing__category__name__icontains=category)
        return self.filter(lookup).is_active().order_by("-created_at")[:10]

class AuctionManager(
    models.Manager.from_queryset(AuctionQuerySet)
):
    pass

class AuctionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    SOLD = 'sold', 'Sold'


class Auction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_price = models.DecimalField( max_digits=10,decimal_places=2,null=True,blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    sold_date = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.PLN)
    processed = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(choices=AuctionStatus.choices, default=AuctionStatus.DRAFT, max_length=10)

    objects = AuctionManager()

    def save(self, *args, **kwargs) -> None:
        if self.current_price is None:
            self.current_price = self.start_price
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']