from rest_framework import serializers

from auction.models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='auction-detail', lookup_field='id')
    class Meta:
        model = Auction
        fields = "__all__"
        read_only_fields = [
            'url',
            "id",
            "current_price",
            "final_price",
            "sold_date",
            "status",
            'currency'
        ]
