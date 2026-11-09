from django.contrib import admin

from rating.models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('author', 'rated_user', 'rating', 'auction', 'created_at')
    list_filter = ('rating',)
    search_fields = ('author__email', 'rated_user__email', 'opinion')
    readonly_fields = ('id', 'created_at', 'updated_at')
