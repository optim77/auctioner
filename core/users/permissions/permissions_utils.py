from listing.models import Listing
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission
from watchlist.models import Watchlist


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self,request,view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOfListing(BasePermission):
    def has_object_permission(self, request, view, obj: Listing):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user == obj.seller)

class IsOwnerOfAuction(BasePermission):

    def has_permission(self, request, view):
        if request.method == "POST":
            listing_id = request.data.get("listing")

            if not listing_id:
                return False

            try:
                listing = Listing.objects.get(id=listing_id)
            except Listing.DoesNotExist:
                return False

            return request.user == listing.seller

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user == obj.listing.seller

class IsOwnerOfWatchlist(BasePermission):
    def has_object_permission(self, request, view, obj: Watchlist):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user == obj.user)

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self,request,view):
        return request.method in permissions.SAFE_METHODS or request.user and request.user.is_authenticated
