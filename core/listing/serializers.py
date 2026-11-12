from rest_framework import serializers

from listing.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('id', 'creation_date', 'seller')
