from datetime import timedelta

import pytest
from auction.models import Auction, AuctionStatus
from categories.models import Category
from django.utils import timezone
from listing.models import Listing
from rest_framework.test import APIClient
from users.models import User, Role
from watchlist.models import Watchlist


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(email='test@test.com', username='test', password='test')

@pytest.fixture
def seller(db):
    return User.objects.create_user(email='seller@test.com', username='seller', password='password')

@pytest.fixture
def bidder(db):
    return User.objects.create_user(email='bidder@test.com', username='bidder', password='password')

@pytest.fixture
def admin(db):
    return User.objects.create_user(email='bidder@test.com', username='bidder', password='password', is_staff=True, role=Role.ADMIN)

@pytest.fixture
def second_bidder(db):
    return User.objects.create_user(email='second_bidder@test.com', username='second_bidder', password='password')

@pytest.fixture
def category(db):
    return Category.objects.create(name='test', items_amount=1)

@pytest.fixture
def second_category(db):
    return Category.objects.create(name='test2')

@pytest.fixture
def watchlist(seller, listing):
    return Watchlist.objects.create(listing=listing, user=seller, notifications_enabled=True)

@pytest.fixture
def listing(seller, category):
    return Listing.objects.create(
        seller=seller,
        name="test",
        description="test",
        creation_date=timezone.now(),
        category=category
    )

@pytest.fixture
def second_listing(seller, category):
    return Listing.objects.create(
        seller=seller,
        name="test",
        description="test",
        creation_date=timezone.now(),
        category=category
    )

@pytest.fixture
def auction(listing):
    return Auction.objects.create(
        listing=listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=1),
        currency="PLN",
        status=AuctionStatus.ACTIVE,
    )

@pytest.fixture
def second_auction(second_listing):
    return Auction.objects.create(
        listing=second_listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=1),
        currency="PLN",
        status=AuctionStatus.ACTIVE,
    )

@pytest.fixture
def auction_ending_soon(second_listing):
    return Auction.objects.create(
        listing=second_listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(minutes=1),
        currency="PLN",
        status=AuctionStatus.ACTIVE,
    )

@pytest.fixture
def draft_auction(listing):
    return Auction.objects.create(
        listing=listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=1),
        currency="PLN",
        status=AuctionStatus.DRAFT,
    )

@pytest.fixture
def expired_auction(listing):
    return Auction.objects.create(
        listing=listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=-1),
        currency="PLN",
        status=AuctionStatus.EXPIRED,
    )

@pytest.fixture
def finished_auction(listing):
    return Auction.objects.create(
        listing=listing,
        start_price=100,
        current_price=100,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(hours=1),
        currency="PLN",
        status=AuctionStatus.SOLD,
    )