from rest_framework import serializers

from rating.models import Rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = (
            'id',
            'author',
            'auction',
            'listing',
            'rated_user',
            'rating',
            'opinion',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'author',
            'listing',
            'rated_user',
            'created_at',
            'updated_at',
        )
