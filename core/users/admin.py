from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-created_at',)
    list_display = ('email', 'username', 'role', 'rating', 'is_staff', 'is_active', 'deleted')
    list_filter = ('role', 'is_staff', 'is_active', 'deleted')
    search_fields = ('email', 'username')
