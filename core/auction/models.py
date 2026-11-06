import uuid
from typing import Self

from bid.utils.currencies import Currency
from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone
from listing.models import Listing
from users.models import User


class AuctionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    SOLD = "sold", "Sold"


class AuctionQuerySet(QuerySet):
    def is_active(self) -> Self:
        """Return only auctions that are currently running."""
        return self.filter(status=AuctionStatus.ACTIVE)

    def is_expired(self) -> Self:
        return self.filter(status=AuctionStatus.EXPIRED)

    def is_sold(self) -> Self:
        return self.filter(status=AuctionStatus.SOLD)

    def ended_before(self, moment=None) -> Self:
        return self.filter(end_date__lte=moment or timezone.now())

    def ending_between(self, start, end) -> Self:
        return self.filter(end_date__gt=start, end_date__lte=end)

    def search(self, query: str) -> Self:
        lookup = Q(listing__name__icontains=query) | Q(
            listing__description__icontains=query
        )
        return self.filter(lookup)

    def newest(self) -> Self:
        return self.order_by("-created_at")

    def hottest(self) -> Self:
        return self.order_by("-bids_counter", "-created_at")

    def with_related(self) -> Self:
        return self.select_related("listing", "winner", "listing__seller")


class Auction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=False, blank=False)
    sold_date = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(
        max_length=3, choices=Currency.choices, default=Currency.PLN
    )
    processed = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)
    winner = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bids_counter = models.PositiveIntegerField(default=0)
    status = models.CharField(
        choices=AuctionStatus.choices,
        default=AuctionStatus.DRAFT,
        max_length=10,
    )

    objects = AuctionQuerySet.as_manager()

    def save(self, *args, **kwargs) -> None:
        if self.current_price is None:
            self.current_price = self.start_price

            update_fields = kwargs.get("update_fields")
            if update_fields is not None and "current_price" not in update_fields:
                kwargs["update_fields"] = [*update_fields, "current_price"]

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.listing} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
