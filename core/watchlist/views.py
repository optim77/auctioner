from django.shortcuts import render
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.permissions.permissions_utils import IsOwnerOfWatchlist
from watchlist.models import Watchlist
from watchlist.serializers.serializers import WatchlistSerializer


class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer
    permission_classes = (IsOwnerOfWatchlist,)
    authentication_classes = (JWTAuthentication,)