from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BaseSerializer

from auction.models import Auction, AuctionStatus
from rating.models import Rating
from users.models import User


class RatingServices:

    @staticmethod
    @transaction.atomic
    def create_rating(serializer: BaseSerializer, user: User) -> Rating:
        """Create a rating for a sold auction won by the requesting user."""
        auction = Auction.objects.select_related(
            'winner', 'listing__seller'
        ).get(id=serializer.validated_data['auction'].id)

        if auction.status != AuctionStatus.SOLD:
            raise ValidationError('Product was not sold!')
        if auction.winner != user:
            raise ValidationError('You didnt bought this product!')
        if Rating.objects.filter(author=user, rated_user=serializer.validated_data['rated_user']).exists():
            raise ValidationError('You already placed a review!')

        seller = auction.listing.seller
        seller.sum_user_rating = True
        seller.save(update_fields=['sum_user_rating'])

        return serializer.save(author=user)
