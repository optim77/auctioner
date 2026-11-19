from uuid import UUID

from listing.models import Listing
from rest_framework.permissions import SAFE_METHODS, BasePermission


def _is_owned_listing(listing_id, user) -> bool:
    """Return True when ``listing_id`` is valid and belongs to ``user``."""
    if not listing_id or not getattr(user, "is_authenticated", False):
        return False

    try:
        UUID(str(listing_id))
    except (TypeError, ValueError, AttributeError):
        return False

    return Listing.objects.filter(id=listing_id, seller=user).exists()


class IsOwnerOfAuction(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS or view.action != "create":
            return True

        return _is_owned_listing(request.data.get("listing"), request.user)

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True

        # Guard against re-assigning an auction to somebody else's listing.
        if "listing" in request.data and not _is_owned_listing(
            request.data["listing"], request.user
        ):
            return False

        return request.user == obj.listing.seller
