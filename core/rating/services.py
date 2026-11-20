from auction.models import Auction, AuctionStatus
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError
from users.models import User

from rating.models import Rating


class RatingService:
    """Write-side operations for ratings."""

    @staticmethod
    @transaction.atomic
    def create_rating(data: dict, user: User, rated_user_id) -> Rating:
        """Create a rating for an auction won by the requesting user.

        The reviewed user and the listing are derived from the auction instead
        of being trusted from the request body.
        """
        auction = Auction.objects.select_related(
            'winner', 'listing__seller'
        ).get(id=data['auction'].id)

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
                return Rating.objects.create(
                    author=user,
                    listing=auction.listing,
                    rated_user=seller,
                    auction=auction,
                    rating=data['rating'],
                    opinion=data.get('opinion', ''),
                )
        except IntegrityError as exc:
            raise ValidationError('You already placed a review!') from exc


RatingServices = RatingService
