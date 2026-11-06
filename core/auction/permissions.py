from listing.models import Listing
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOfAuction(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method == "POST":
            listing_id = request.data.get("listing")

            if not listing_id:
                return False

            try:
                listing = Listing.objects.get(id=listing_id)
            except Listing.DoesNotExist:
                return False

            return bool(request.user == listing.seller)

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.listing.seller
