from rest_framework import viewsets

from listing.models import Listing
from listing.permissions import IsOwnerOfListing
from listing.serializers import ListingSerializer
from listing.services import ListingService


class ListingViewSet(viewsets.ModelViewSet):
    """CRUD for listings; every mutation is owned by the requesting user."""

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOfListing]

    def perform_create(self, serializer) -> None:
        # DRF reads ``serializer.data`` after this hook, so the created object
        # must be attached to the serializer instead of merely returned.
        serializer.instance = ListingService.create_listing(
            serializer.validated_data, self.request.user
        )

    def perform_update(self, serializer) -> Listing:
        return ListingService.update_listing(
            serializer.instance, serializer.validated_data, self.request.user
        )

    def perform_destroy(self, instance) -> None:
        ListingService.destroy_listing(instance)
