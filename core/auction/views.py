from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from auction.selectors import newest_auction, newest_auction_in_category, search_auction, get_hot_auctions
from users.permissions.permissions_utils import IsOwnerOfAuction

from auction.models import Auction
from auction.serializers import AuctionSerializer
from auction.services import AuctionServices


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfAuction]
    lookup_field = 'id'

    def get_queryset(self):
        search = self.request.query_params.get("q")
        return search_auction(search) if search else Auction.objects.is_active()


    @action(detail=True, methods=['post'])
    def activate(self, pk=None) -> Response:
        auction = AuctionServices.activate(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def finish(self, pk=None) -> Response:
        auction = AuctionServices.finish(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def expire(self, pk=None) -> Response:
        auction = AuctionServices.expire(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

class NewestAuctionViewSet(generics.ListAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        return newest_auction()


class NewestInCategoryViewSet(generics.ListAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        category = self.request.query_params.get("category")
        return  newest_auction_in_category(category=category) if category else Auction.objects.none()


class HotAuctionViewSet(generics.ListAPIView):
    serializer_class  = AuctionSerializer

    def get_queryset(self):
        return get_hot_auctions()

