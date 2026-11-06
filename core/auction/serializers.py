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
            "currency",
            "winner",
            "bids_counter",
            "processed",
            "processing",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_price = attrs.get(
            "start_price", getattr(self.instance, "start_price", None)
        )
        start_date = attrs.get(
            "start_date", getattr(self.instance, "start_date", None)
        )
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start_price is not None and start_price <= 0:
            raise serializers.ValidationError(
                {"start_price": "Start price must be greater than zero."}
            )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be later than start date."}
            )

        return attrs
