from decimal import Decimal

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
        extra_kwargs = {"bid_price": {"min_value": Decimal("0.01")}}