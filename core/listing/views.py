from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from listing.models import Listing
from listing.permissions import IsOwnerOfListing
from listing.serializers import ListingSerializer
from listing.services import ListingServices


class ListingViewSet(viewsets.ModelViewSet):
    """CRUD for listings; every mutation is owned by the requesting user."""

    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfListing]

    def perform_create(self, serializer) -> Listing:
        return ListingServices.create_listing(serializer, self.request.user)

    def perform_update(self, serializer) -> Listing:
        return ListingServices.update_listing(serializer, self.request.user)

    def perform_destroy(self, instance) -> None:
        ListingServices.destroy_listing(instance)
