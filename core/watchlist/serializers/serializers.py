from rest_framework import serializers

from watchlist.models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = '__all__'
