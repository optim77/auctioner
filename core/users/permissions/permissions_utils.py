from listing.models import Listing
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission

from rating.models import Rating
from users.models import User
from watchlist.models import Watchlist
from auction.models import Auction


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self,request,view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOfListing(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user == obj.seller
        )

class IsOwnerOfRating(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.author

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

class IsOwnerOfWatchlist(BasePermission):
    def has_object_permission(self, request, view, obj: Watchlist) -> bool:
        return bool(request.user and request.user == obj.user)

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self,request,view) -> bool:
        return request.method in permissions.SAFE_METHODS or request.user and request.user.is_authenticated

class IsAccountOwner(BasePermission):
    def has_object_permission(self, request, view, obj: User) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and  request.user == obj)


class IsWonAuctionsOwner(BasePermission):
    def has_object_permission(self, request, view, obj: Auction) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user == obj.winner)
