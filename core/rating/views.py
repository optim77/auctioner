from django.db import transaction
from rest_framework import viewsets, serializers
from rest_framework.exceptions import ValidationError

from auction.models import Auction, AuctionStatus
from rating.models import Rating
from rating.serializers.serializers import RatingSerializer
from users.permissions.permissions_utils import IsOwnerOfRating


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    permission_classes = [IsOwnerOfRating]
    serializer_class = RatingSerializer

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return Rating.objects.filter(rated_user=self.kwargs['user_id'])


    def perform_create(self, serializer):
        user_auction = serializer.validated_data['auction']
        db_auction = Auction.objects.filter(id=user_auction.id).first()
        if db_auction.status != AuctionStatus.SOLD:
            raise ValidationError('Product was not sold!')
        if db_auction.winner != self.request.user:
            raise ValidationError('You didnt bought this product!')
        rating = Rating.objects.filter(author=self.request.user, rated_user=serializer.validated_data['rated_user']).first()
        if rating:
            raise ValidationError('You already placed a review!')
        db_auction.listing.seller.sum_user_rating = True

        rating = serializer.save(author=self.request.user)
        return rating


