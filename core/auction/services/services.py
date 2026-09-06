from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from auction.models import Auction, AuctionStatus



class AuctionServices:

    @staticmethod
    @transaction.atomic
    def activate(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.ACTIVE:
            raise ValidationError('Auction is already active')
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Cannot activate sold auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Cannot activate expired auction')
        auction.status = AuctionStatus.ACTIVE
        if auction.current_price is None:
            auction.current_price = auction.start_price

        auction.status = AuctionStatus.ACTIVE
        auction.save(update_fields=["status", "current_price"])

    @staticmethod
    @transaction.atomic
    def finish(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.DRAFT:
            raise ValidationError('Cannot sell draft auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Cannot finish expired auction')
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Auction is already sold')
        auction.status = AuctionStatus.SOLD
        auction.save(update_fields=['status'])
        return auction

    @staticmethod
    @transaction.atomic
    def expire(auction_id):
        auction = (Auction.objects.select_for_update().get(id=auction_id))
        if auction.status == AuctionStatus.SOLD:
            raise ValidationError('Cannot expire sold auction')
        if auction.status == AuctionStatus.EXPIRED:
            raise ValidationError('Auction is already expired')
        if auction.status == AuctionStatus.DRAFT:
            raise ValidationError('Cannot expire draft auction')
        auction.status = AuctionStatus.EXPIRED
        auction.save(update_fields=['status'])
        return auction

    @staticmethod
    @transaction.atomic
    def expire_auctions():
        expired_auctions = Auction.objects.select_for_update().filter(
            status=AuctionStatus.ACTIVE,
            end_date__lte=timezone.now()
        )
        for auction in expired_auctions:
            auction.status = AuctionStatus.EXPIRED
            auction.save(update_fields=["status"])