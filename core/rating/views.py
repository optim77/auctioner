from django.db import transaction
from rest_framework import viewsets, serializers

from auction.models import Auction, AuctionStatus
from rating.models import Rating
from rating.serializers.serializers import RatingSerializer
from users.permissions.permissions_utils import IsOwnerOfRating


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsOwnerOfRating]
    serializer_class = RatingSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        user_auction = serializer.validated_data['auction']
        db_auction = Auction.objects.filter(id=user_auction.id).first()
        if db_auction.status is not AuctionStatus.SOLD:
            raise serializers.ValidationError({'error': 'Product was not sold!'})
        if db_auction.winner is not self.request.user:
            raise serializers.ValidationError({'error': 'You didnt bought this product!'})

