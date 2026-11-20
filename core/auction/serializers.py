from rest_framework import serializers

from auction.models import Auction, AuctionStatus


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = [
            "id",
            "listing",
            "start_price",
            "current_price",
            "final_price",
            "start_date",
            "end_date",
            "sold_date",
            "currency",
            "winner",
            "bids_counter",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "current_price",
            "final_price",
            "sold_date",
            "winner",
            "bids_counter",
            "status",
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

        if self.instance is not None:
            if "listing" in attrs and attrs["listing"] != self.instance.listing:
                raise serializers.ValidationError(
                    {"listing": "Auction listing cannot be changed."}
                )

            if self.instance.status != AuctionStatus.DRAFT:
                for field in ("start_price", "start_date", "end_date"):
                    if field in attrs and attrs[field] != getattr(self.instance, field):
                        raise serializers.ValidationError(
                            {
                                field: (
                                    "Price and dates cannot be changed after "
                                    "the auction has been activated."
                                )
                            }
                        )

        return attrs
