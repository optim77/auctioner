"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers

from auction.views import AuctionViewSet
from bid.views import BidViewSet
from categories.views import CategoryViewSet
from listing.views import ListingViewSet
from watchlist.views import WatchlistViewSet

router = routers.DefaultRouter()
router.register(r'auctions', AuctionViewSet, basename='auction')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'listing', ListingViewSet, basename='listing')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path(
        'auctions/<uuid:auction_id>/bids/',
        BidViewSet.as_view({"post": "create"}),
        name='bid',
    ),
    path('', include(router.urls)),
    path("auth/", include("users.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
