from django.contrib import admin

from auction.models import Auction


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "status",
        "current_price",
        "currency",
        "end_date",
        "bids_counter",
    )
    list_filter = ("status", "currency")
    search_fields = ("listing__name", "listing__seller__username")
    readonly_fields = ("id", "created_at", "updated_at", "bids_counter")
    date_hierarchy = "created_at"
