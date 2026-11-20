from categories.services import (
    decrement_category_items_count,
    increment_category_items_count,
)
from django.db import transaction
from users.models import User

from listing.models import Listing


class ListingService:
    """Write-side operations for listings.

    Services take validated plain data, not DRF serializers, so they can be
    reused from views, tasks, management commands or tests.
    """

    @staticmethod
    @transaction.atomic
    def create_listing(data: dict, user: User) -> Listing:
        """Create a listing owned by ``user`` and bump its category counter."""
        data = {key: value for key, value in data.items() if key != "seller"}
        listing = Listing.objects.create(**data, seller=user)
        increment_category_items_count(listing.category_id)
        return listing

    @staticmethod
    @transaction.atomic
    def update_listing(listing: Listing, data: dict, user: User) -> Listing:
        """Update a listing owned by ``user``, moving its category counter."""
        old_category_id = listing.category_id

        for field, value in data.items():
            if field != "seller":
                setattr(listing, field, value)
        listing.seller = user
        listing.save()

        if listing.category_id != old_category_id:
            if old_category_id:
                decrement_category_items_count(old_category_id)
            if listing.category_id:
                increment_category_items_count(listing.category_id)

        return listing

    @staticmethod
    @transaction.atomic
    def destroy_listing(listing: Listing) -> None:
        """Delete a listing and drop its category counter."""
        decrement_category_items_count(listing.category_id)
        listing.delete()


# Backwards-compatible alias for code written against the old name.
ListingServices = ListingService
