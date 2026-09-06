from rest_framework import serializers

from bid.models import Bid


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = [
            "id",
            "bid_price",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]