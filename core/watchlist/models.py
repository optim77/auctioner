import uuid

from django.db import models
from listing.models import Listing
from users.models import User


class Watchlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    notifications_enabled = models.BooleanField(default=True)


    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['listing', 'user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'user'],
                name='unique_watchlist_listing_user',
            ),
        ]
