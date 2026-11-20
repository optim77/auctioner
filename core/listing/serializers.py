from rest_framework import serializers

from listing.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            'id',
            'seller',
            'name',
            'description',
            'creation_date',
            'category',
            'images',
        ]
        read_only_fields = ('id', 'creation_date', 'seller')
