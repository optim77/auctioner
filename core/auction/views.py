from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from auction.models import Auction
from auction.permissions import IsOwnerOfAuction
from auction.selectors import (
    get_active_auctions,
    get_hot_auctions,
    get_newest_auctions,
    get_newest_auctions_in_category,
    search_auctions,
)
from auction.serializers import AuctionSerializer
from auction.services import AuctionServices


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfAuction]
    lookup_field = "id"

    def get_queryset(self):
        if self.action != "list":
            return Auction.objects.with_related()

        search = self.request.query_params.get("q")
        if search:
            return search_auctions(search)

        return get_active_auctions()

    def _run_transition(self, service) -> Response:
        auction = service(self.get_object().id)
        return Response(
            self.get_serializer(auction).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, id=None) -> Response:
        return self._run_transition(AuctionServices.activate)

    @action(detail=True, methods=["post"])
    def finish(self, request, id=None) -> Response:
        return self._run_transition(AuctionServices.finish)

    @action(detail=True, methods=["post"])
    def expire(self, request, id=None) -> Response:
        return self._run_transition(AuctionServices.expire)


class NewestAuctionViewSet(generics.ListAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        return get_newest_auctions()


class NewestInCategoryViewSet(generics.ListAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        category = self.kwargs.get("category") or self.request.query_params.get(
            "category"
        )
        if not category:
            return Auction.objects.none()

        return get_newest_auctions_in_category(category)


class HotAuctionViewSet(generics.ListAPIView):
    serializer_class = AuctionSerializer

    def get_queryset(self):
        return get_hot_auctions()
