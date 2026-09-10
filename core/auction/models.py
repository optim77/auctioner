import uuid

from django.db import models

from bid.utils.currencies import Currency
from listing.models import Listing

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

    status = models.CharField(choices=AuctionStatus.choices, default=AuctionStatus.DRAFT, max_length=10)

    def save(self, *args, **kwargs):
        if self.current_price is None:
            self.current_price = self.start_price
        super().save(*args, **kwargs)
