from django.urls import path

from listing.views import ListingViewSet

urlpatterns = [
    path('listing/', ListingViewSet.as_view()),
]