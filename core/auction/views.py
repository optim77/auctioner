from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from auction.models import Auction
from auction.serializers.serializers import AuctionSerializer
from auction.services.services import AuctionServices
from users.permissions.permissions_utils import IsOwnerOfAuction


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfAuction]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        auction = AuctionServices.activate(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        auction = AuctionServices.finish(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def expire(self, request, pk=None):
        auction = AuctionServices.expire(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )