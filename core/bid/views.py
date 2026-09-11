from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from bid.serializers.serializers import BidSerializer
from bid.services.bid_service import BidService


class BidViewSet(viewsets.GenericViewSet):
    serializer_class = BidSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, auction_id=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bid = BidService.place_bid(
            auction_id=auction_id,
            bidder=request.user,
            bid_price=serializer.validated_data["bid_price"],
        )

        return Response(
            self.get_serializer(bid).data,
            status=status.HTTP_201_CREATED,
        )