from django.db.models import QuerySet
from rest_framework import viewsets

from rating.models import Rating
from rating.permissions import IsOwnerOfRating
from rating.serializers import RatingSerializer
from rating.services import RatingServices


class RatingViewSet(viewsets.ModelViewSet):
    """Ratings received by a specific user (``/rating/<user_id>/``)."""

    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsOwnerOfRating]

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self) -> QuerySet[Rating]:
        return Rating.objects.filter(rated_user_id=self.kwargs['user_id'])

    def perform_create(self, serializer) -> None:
        RatingServices.create_rating(serializer, self.request.user)
