from rest_framework import serializers

from watchlist.models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'
        ordering = ('-created_at',)
        read_only_fields = ('id',)
