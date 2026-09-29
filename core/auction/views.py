from django.db.models import QuerySet
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions.permissions_utils import IsOwnerOfAuction

from auction.models import Auction
from auction.serializers.serializers import AuctionSerializer
from auction.services.services import AuctionServices


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfAuction]
    lookup_field = 'id'

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("q")
        if search:
            qs = qs.search(search)
        return qs


    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None) -> Response:
        auction = AuctionServices.activate(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None) -> Response:
        auction = AuctionServices.finish(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def expire(self, request, pk=None) -> Response:
        auction = AuctionServices.expire(pk)
        return Response(
            AuctionSerializer(auction), status=status.HTTP_200_OK
        )

class NewestAuctionViewSet(generics.ListAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.newest_auction()


class NewestInCategoryViewSet(generics.ListAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

    def get_queryset(self):
        category = self.request.query_params.get("category")
        qs = Auction.objects.none()
        if category:
            qs = super().get_queryset();
            return qs.newest_auction_in_category()
        return qs


class HotAuctionViewSet(generics.ListAPIView):
    queryset = Auction.objects.all()
    class_serializer_class = AuctionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.most_bids()

