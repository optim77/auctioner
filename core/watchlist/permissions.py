from rest_framework.permissions import BasePermission

from watchlist.models import Watchlist


class IsOwnerOfWatchlist(BasePermission):
    def has_object_permission(self, request, view, obj: Watchlist) -> bool:
        return bool(request.user and request.user == obj.user)
