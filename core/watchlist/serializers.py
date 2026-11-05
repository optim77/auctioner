from rest_framework import serializers

from watchlist.models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ('id', 'user', 'listing', 'auction', 'notifications_enabled', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
