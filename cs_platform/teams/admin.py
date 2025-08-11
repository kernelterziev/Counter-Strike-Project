from django.contrib import admin
from .models import Team, TeamMembership

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'country', 'captain', 'founded_date', 'is_active']
    list_filter = ['country', 'is_active', 'founded_date']
    search_fields = ['name', 'tag', 'captain__username']
    ordering = ['-founded_date']

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['player', 'team', 'role', 'joined_date', 'is_active']
    list_filter = ['role', 'is_active', 'joined_date']
    search_fields = ['player__username', 'team__name']