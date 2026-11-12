from django.db import transaction
from rest_framework.serializers import BaseSerializer

from categories.services import decrement_category_items_count, increment_category_items_count
from listing.models import Listing
from users.models import User


class ListingServices:

    @staticmethod
    @transaction.atomic
    def create_listing(serializer: BaseSerializer, user: User) -> Listing:
        """Create a listing owned by ``user`` and bump its category counter."""
        listing = serializer.save(seller=user)
        increment_category_items_count(listing.category_id)
        return listing

    @staticmethod
    @transaction.atomic
    def update_listing(serializer: BaseSerializer, user: User) -> Listing:
        """Update a listing owned by ``user``, moving its category counter."""
        old_category_id = serializer.instance.category_id
        listing = serializer.save(seller=user)

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
