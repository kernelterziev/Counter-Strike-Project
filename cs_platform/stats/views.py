from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Sum, Avg, Count, F, Q
from django.contrib.auth import get_user_model
from .models import WeaponStats, MapStats
from matches.models import PlayerMatchStats
from teams.models import Team

User = get_user_model()


# Class-based view for weapon statistics
class WeaponStatsView(ListView):
    model = WeaponStats
    template_name = 'stats/weapon_stats.html'
    context_object_name = 'weapon_stats'
    paginate_by = 50
    ordering = ['-total_kills']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('player')
        weapon_filter = self.request.GET.get('weapon')

        if weapon_filter:
            queryset = queryset.filter(weapon=weapon_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weapon_choices'] = WeaponStats.WEAPON_CHOICES
        context['current_weapon'] = self.request.GET.get('weapon', 'all')

        # Top weapons by total kills
        context['top_weapons'] = WeaponStats.objects.values('weapon').annotate(
            total=Sum('total_kills')
        ).order_by('-total')[:5]

        return context


# Class-based view for map statistics
class MapStatsView(ListView):
    model = MapStats
    template_name = 'stats/map_stats.html'
    context_object_name = 'map_stats'
    paginate_by = 50
    ordering = ['-matches_played']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('player')
        map_filter = self.request.GET.get('map')

        if map_filter:
            queryset = queryset.filter(map_name=map_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['map_choices'] = MapStats.MAP_CHOICES
        context['current_map'] = self.request.GET.get('map', 'all')

        # Most popular maps
        context['popular_maps'] = MapStats.objects.values('map_name').annotate(
            total_matches=Sum('matches_played')
        ).order_by('-total_matches')[:7]

        return context


# Function-based view for leaderboard
def leaderboard(request):
    """Global leaderboard with various statistics"""

    # Top players by total kills
    top_killers = User.objects.annotate(
        total_kills=Sum('match_stats__kills'),
        total_deaths=Sum('match_stats__deaths'),
        total_matches=Count('match_stats'),
        avg_kills=Avg('match_stats__kills')
    ).filter(
        total_kills__gt=0
    ).order_by('-total_kills')[:10]

    # Calculate K/D ratios
    for player in top_killers:
        if player.total_deaths and player.total_deaths > 0:
            player.kd_ratio = round(player.total_kills / player.total_deaths, 2)
        else:
            player.kd_ratio = player.total_kills

    # Top teams by wins (placeholder - would need match results)
    top_teams = Team.objects.filter(is_active=True).annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('-founded_date')[:10]

    # Most active players
    most_active = User.objects.annotate(
        match_count=Count('match_stats')
    ).filter(match_count__gt=0).order_by('-match_count')[:10]

    # Weapon preferences
    weapon_popularity = WeaponStats.objects.values('weapon').annotate(
        total_kills=Sum('total_kills'),
        user_count=Count('player', distinct=True)
    ).filter(total_kills__gt=0).order_by('-total_kills')[:5]

    # Map preferences
    map_popularity = MapStats.objects.values('map_name').annotate(
        total_matches=Sum('matches_played'),
        user_count=Count('player', distinct=True)
    ).filter(total_matches__gt=0).order_by('-total_matches')[:7]

    context = {
        'top_killers': top_killers,
        'top_teams': top_teams,
        'most_active': most_active,
        'weapon_popularity': weapon_popularity,
        'map_popularity': map_popularity,
        'total_players': User.objects.count(),
        'total_teams': Team.objects.filter(is_active=True).count(),
        'total_matches': PlayerMatchStats.objects.values('match').distinct().count(),
    }

    return render(request, 'stats/leaderboard.html', context)