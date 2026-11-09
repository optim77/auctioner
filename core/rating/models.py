from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from auction.models import Auction
from listing.models import Listing
from users.models import User
from utils.base_model import BaseModel


class Rating(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    opinion = models.TextField(validators=[MaxLengthValidator(1000)])
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='ratings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.listing.name)

    class Meta:
        ordering = ['-created_at']
