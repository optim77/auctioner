from django.contrib import admin

from listing.models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'creation_date')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'seller__email')
    readonly_fields = ('creation_date',)
