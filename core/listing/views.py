from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.models import Category
from listing.models import Listing
from listing.serializers.serializers import ListingSerializer
from users.permissions.permissions_utils import IsOwnerOfListing


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOfListing]

    @transaction.atomic
    def perform_create(self, serializer):
        category = serializer.validated_data['category']
        Category.objects.filter(id=category.id).update(items_amount=F('items_amount') + 1)
        serializer.save()

    @transaction.atomic
    def perform_destroy(self, serializer):
        category = serializer.validated_data['category']
        Category.objects.filter(id=category.id).update(items_amount=F('items_amount') - 1)
        serializer.delete()

