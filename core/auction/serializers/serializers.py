from rest_framework import serializers

from auction.models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = "__all__"
        read_only_fields = [
            "id",
            "current_price",
            "final_price",
            "sold_date",
            "status",
            'start_date',
            'currency'
        ]
