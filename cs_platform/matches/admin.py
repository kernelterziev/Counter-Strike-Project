from django.contrib import admin
from .models import Match, PlayerMatchStats

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['team1', 'team2', 'map_name', 'team1_score', 'team2_score', 'match_date', 'is_finished']
    list_filter = ['map_name', 'match_type', 'is_finished', 'match_date']
    search_fields = ['team1__name', 'team2__name']
    ordering = ['-match_date']

@admin.register(PlayerMatchStats)
class PlayerMatchStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'kills', 'deaths', 'assists', 'kd_ratio']
    list_filter = ['match__map_name', 'team']
    search_fields = ['player__username', 'match__team1__name', 'match__team2__name']