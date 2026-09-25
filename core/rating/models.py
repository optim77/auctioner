import uuid

from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.db import models

from auction.models import Auction
from listing.models import Listing
from users.models import User


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rated_user')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.TextField(validators=[MaxLengthValidator(1000)])
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='auction')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.listing.name)

    class Meta:
        ordering = ['-created_at']