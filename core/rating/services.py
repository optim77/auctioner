from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BaseSerializer

from auction.models import Auction, AuctionStatus
from rating.models import Rating
from users.models import User


class RatingServices:

    @staticmethod
    @transaction.atomic
    def create_rating(
        serializer: BaseSerializer, user: User, rated_user_id
    ) -> Rating:
        """Create a rating for an auction won by the requesting user.

        The reviewed user and the listing are derived from the auction instead
        of being trusted from the request body.
        """
        auction = Auction.objects.select_related(
            'winner', 'listing__seller'
        ).get(id=serializer.validated_data['auction'].id)

        if auction.status != AuctionStatus.SOLD:
            raise ValidationError('Product was not sold!')
        if auction.winner_id != user.id:
            raise ValidationError('You didnt bought this product!')

        seller = auction.listing.seller
        if str(seller.id) != str(rated_user_id):
            raise ValidationError('You can only rate the seller of the auction.')
        if seller.id == user.id:
            raise ValidationError('You cannot rate yourself.')
        if Rating.objects.filter(auction=auction, author=user).exists():
            raise ValidationError('You already placed a review!')

        try:
            with transaction.atomic():
                return serializer.save(
                    author=user,
                    listing=auction.listing,
                    rated_user=seller,
                )
        except IntegrityError as exc:
            raise ValidationError('You already placed a review!') from exc
