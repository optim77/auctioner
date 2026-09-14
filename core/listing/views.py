from categories.models import Category
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions.permissions_utils import IsOwnerOfListing

from listing.models import Listing
from listing.serializers.serializers import ListingSerializer


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
    def perform_update(self, serializer):
        listing = serializer.instance
        old_category = listing.category
        serializer.save()
        new_category = listing.category
        if old_category != new_category:
            Category.objects.filter(pk=old_category.pk).update(
                items_amount=F('items_amount') - 1
            )
            Category.objects.filter(pk=new_category.pk).update(
                items_amount=F('items_amount') + 1
            )

    @transaction.atomic
    def perform_destroy(self, instance):
        category = instance.category
        Category.objects.filter(id=category.id).update(
            items_amount=F('items_amount') - 1
        )
        instance.delete()

