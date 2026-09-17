from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from bid.serializers.serializers import BidSerializer
from bid.services.services import BidService


class BidViewSet(viewsets.GenericViewSet):
    serializer_class = BidSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request: Request, auction_id: UUID | None = None) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if auction_id and request.user:
            bid = BidService.place_bid(
                auction_id=auction_id,
                bidder=request.user,
                bid_price=serializer.validated_data["bid_price"],
            )

            return Response(
                self.get_serializer(bid).data,
                status=status.HTTP_201_CREATED,
            )
        raise ValidationError({"auction_id": "This field is required."})