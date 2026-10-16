from django.db import transaction
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.services import increment_category_items_count, decrement_category_items_count
from users.permissions.permissions_utils import IsOwnerOfListing

from listing.models import Listing
from listing.serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfListing]

    @transaction.atomic
    def perform_create(self, serializer) -> Listing:
        category = serializer.validated_data['category']
        increment_category_items_count(category.id)
        listing = serializer.save(seller=self.request.user)
        return listing

    @transaction.atomic
    def perform_update(self, serializer) -> Listing:
        listing = serializer.instance
        old_category = listing.category
        saved_listing = serializer.save(seller=self.request.user)
        new_category = listing.category
        if old_category != new_category:
            decrement_category_items_count(old_category.id)
            increment_category_items_count(new_category.id)
        return saved_listing

    @transaction.atomic
    def perform_destroy(self, instance) -> None:
        category = instance.category
        decrement_category_items_count(category.id)
        instance.delete()