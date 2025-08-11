from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'rank', 'hours_played', 'country', 'is_staff']
    list_filter = ['rank', 'country', 'is_premium', 'date_joined']
    search_fields = ['username', 'email', 'country']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('CS Info', {'fields': ('rank', 'hours_played', 'favorite_weapon', 'avatar', 'country', 'bio', 'is_premium')}),
    )