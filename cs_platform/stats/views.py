from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Sum, Avg, Count, F, Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
import random
import hashlib
from .models import WeaponStats, MapStats
from matches.models import PlayerMatchStats, Match
from teams.models import Team

User = get_user_model()

def set_mock_seed():
    """Set consistent seed for reproducible mock data"""
    random.seed(42)

# Enhanced Player Comparison Tool
def player_comparison(request):
    print("=== DEBUG INFO ===")
    print(f"GET params: {request.GET}")
    print(f"Player1 ID: '{request.GET.get('player1')}'")
    print(f"Player2 ID: '{request.GET.get('player2')}'")

    player1_id = request.GET.get('player1')
    player2_id = request.GET.get('player2')

    player1 = None
    player2 = None
    comparison_data = None

    if player1_id and player2_id:
        print(f"Both players selected! Looking for ID {player1_id} and {player2_id}")
        try:
            player1 = get_object_or_404(User, id=player1_id)
            player2 = get_object_or_404(User, id=player2_id)
            print(f"Found players: {player1.username} and {player2.username}")

            # Generate comparison data
            comparison_data = generate_player_comparison(player1, player2)
            print(f"Generated comparison data: {bool(comparison_data)}")

        except Exception as e:
            print(f"ERROR finding players: {e}")
            player1 = player2 = None
    else:
        print("Not both players selected!")

    # Get all players for selection
    all_players = User.objects.filter(
        Q(match_stats__isnull=False) | Q(is_professional=True)
    ).distinct().order_by('username')[:35]

    context = {
        'player1': player1,
        'player2': player2,
        'comparison_data': comparison_data,
        'all_players': all_players,
    }

    return render(request, 'stats/player_comparison.html', context)


def generate_player_comparison(player1, player2):
    """Generate comprehensive comparison data between two players"""

    # Basic stats with mock data enhancement
    def get_enhanced_player_stats(player):
        # Real stats from database
        real_stats = player.match_stats.aggregate(
            total_kills=Sum('kills'),
            total_deaths=Sum('deaths'),
            total_assists=Sum('assists'),
            total_headshots=Sum('headshots'),
            total_damage=Sum('damage_dealt'),
            match_count=Count('match')
        )

        # Fix None values to 0
        for key, value in real_stats.items():
            if value is None:
                real_stats[key] = 0

        # Enhanced with realistic mock data if low/no real data
        if real_stats['match_count'] < 5:
            # Generate realistic stats for demo
            base_matches = max(real_stats['match_count'], 15)
            mock_stats = {
                'total_kills': real_stats['total_kills'] + (base_matches * 18),  # ~18 kills per match
                'total_deaths': real_stats['total_deaths'] + (base_matches * 14),  # ~14 deaths per match
                'total_assists': real_stats['total_assists'] + (base_matches * 6),  # ~6 assists per match
                'total_headshots': real_stats['total_headshots'] + (base_matches * 8),  # ~44% HS rate
                'total_damage': real_stats['total_damage'] + (base_matches * 2300),  # ~2300 ADR
                'match_count': base_matches
            }
            return mock_stats

        return real_stats

    # Get enhanced stats for both players
    p1_stats = get_enhanced_player_stats(player1)
    p2_stats = get_enhanced_player_stats(player2)

    # Calculate derived stats
    def calculate_derived_stats(stats):
        derived = {}
        derived['kd_ratio'] = round(stats['total_kills'] / max(stats['total_deaths'], 1), 2)
        derived['adr'] = round(stats['total_damage'] / max(stats['match_count'], 1), 1)
        derived['kpr'] = round(stats['total_kills'] / max(stats['match_count'], 1), 1)
        derived['hs_percentage'] = round((stats['total_headshots'] / max(stats['total_kills'], 1)) * 100, 1)
        derived['assists_per_match'] = round(stats['total_assists'] / max(stats['match_count'], 1), 1)
        return derived

    p1_derived = calculate_derived_stats(p1_stats)
    p2_derived = calculate_derived_stats(p2_stats)

    # Mock weapon preferences
    weapon_preferences = {
        player1.id: [
            {'weapon': 'AK-47', 'kills': p1_stats['total_kills'] // 3, 'percentage': 33.2},
            {'weapon': 'M4A4', 'kills': p1_stats['total_kills'] // 4, 'percentage': 25.1},
            {'weapon': 'AWP', 'kills': p1_stats['total_kills'] // 8, 'percentage': 12.8},
        ],
        player2.id: [
            {'weapon': 'AK-47', 'kills': p2_stats['total_kills'] // 3, 'percentage': 31.8},
            {'weapon': 'AWP', 'kills': p2_stats['total_kills'] // 5, 'percentage': 19.2},
            {'weapon': 'M4A1-S', 'kills': p2_stats['total_kills'] // 4, 'percentage': 24.3},
        ]
    }

    # Mock map performance
    map_performance = {
        player1.id: [
            {'map': 'Dust 2', 'matches': 25, 'wins': 16, 'win_rate': 64.0, 'avg_kills': 19.2, 'kd': 1.34},
            {'map': 'Mirage', 'matches': 22, 'wins': 12, 'win_rate': 54.5, 'avg_kills': 17.8, 'kd': 1.18},
            {'map': 'Inferno', 'matches': 18, 'wins': 11, 'win_rate': 61.1, 'avg_kills': 18.5, 'kd': 1.28},
            ],
        player2.id: [
            {'map': 'Mirage', 'matches': 28, 'wins': 18, 'win_rate': 64.3, 'avg_kills': 20.1, 'kd': 1.42},
            {'map': 'Dust 2', 'matches': 24, 'wins': 13, 'win_rate': 54.2, 'avg_kills': 18.7, 'kd': 1.21},
            {'map': 'Inferno', 'matches': 20, 'wins': 14, 'win_rate': 70.0, 'avg_kills': 19.8, 'kd': 1.51},
        ]
    }

    # Team history
    team_history = {
        player1.id: [
            {'team': 'Team Vitality', 'period': '2024-2025', 'matches': 45, 'wins': 28},
            {'team': 'MOUZ', 'period': '2023-2024', 'matches': 67, 'wins': 38},
            {'team': 'BIG', 'period': '2022-2023', 'matches': 52, 'wins': 24},
        ],
        player2.id: [
            {'team': 'NAVI', 'period': '2024-2025', 'matches': 42, 'wins': 31},
            {'team': 'G2 Esports', 'period': '2023-2024', 'matches': 58, 'wins': 34},
            {'team': 'FaZe Clan', 'period': '2022-2023', 'matches': 61, 'wins': 35},
        ]
    }

    return {
        'basic_stats': {
            player1.id: {**p1_stats, **p1_derived},
            player2.id: {**p2_stats, **p2_derived}
        },
        'weapon_preferences': weapon_preferences,
        'map_performance': map_performance,
        'team_history': team_history,
    }


# Enhanced Match History for Teams
def team_match_history(request, team_id):
    """Show enhanced match history for a team with last 5 matches"""
    team = get_object_or_404(Team, id=team_id)

    # Get real matches
    real_matches = Match.objects.filter(
        Q(team1=team) | Q(team2=team)
    ).order_by('-match_date')[:2]  # Get only 2 real matches

    # Generate 3 additional realistic mock matches
    mock_matches = generate_mock_matches(team)

    # Combine real and mock matches
    all_matches = list(real_matches) + mock_matches

    # Team statistics
    team_stats = calculate_team_stats(team, all_matches)

    context = {
        'team': team,
        'matches': all_matches[:3],  # Show only last 5
        'team_stats': team_stats,
    }

    return render(request, 'stats/team_match_history.html', context)


def generate_mock_matches(team):
    """Generate realistic mock matches for demo purposes"""
    from random import choice, randint

    # Realistic opponent teams
    opponent_pools = [
        'Team Vitality', 'NAVI', 'G2 Esports', 'FaZe Clan', 'MOUZ',
        'BIG', 'Team Spirit', 'Cloud9', 'FURIA', 'Heroic',
        'ENCE', 'OG', 'Ninjas in Pyjamas', 'Astralis', 'Complexity'
    ]

    maps = ['dust2', 'mirage', 'inferno', 'cache', 'overpass', 'train']

    mock_matches = []

    for i in range(3):
        # Create mock match
        days_ago = (i + 1) * 2  # 2, 4, 6 days ago
        match_date = timezone.now() - timedelta(days=days_ago)

        opponent_name = choice(opponent_pools)
        map_name = choice(maps)

        # Realistic scores
        team_score = randint(13, 16)
        opponent_score = randint(10, 16)

        # Make it more realistic - closer scores
        if abs(team_score - opponent_score) > 3:
            if team_score > opponent_score:
                opponent_score = team_score - randint(1, 3)
            else:
                team_score = opponent_score - randint(1, 3)

        # Create mock match object
        mock_match = type('MockMatch', (), {
            'id': f'mock_{i}',
            'team1': team,
            'team2': type('MockTeam', (), {'name': opponent_name, 'tag': f'[{opponent_name[:3].upper()}]'}),
            'map_name': map_name,
            'team1_score': team_score,
            'team2_score': opponent_score,
            'match_date': match_date,
            'match_type': 'competitive',
            'is_finished': True,
            'duration_minutes': randint(35, 65),
            'is_mock': True,  # Flag to identify mock matches
        })

        # Add winner property
        mock_match.winner = mock_match.team1 if team_score > opponent_score else mock_match.team2

        mock_matches.append(mock_match)

    return mock_matches


def calculate_team_stats(team, matches):
    """Calculate team statistics from matches"""
    if not matches:
        return {}

    wins = 0
    total_rounds_for = 0
    total_rounds_against = 0

    for match in matches:
        if hasattr(match, 'is_mock') and match.is_mock:
            # Mock match
            if match.team1 == team:
                total_rounds_for += match.team1_score
                total_rounds_against += match.team2_score
                if match.team1_score > match.team2_score:
                    wins += 1
            else:
                total_rounds_for += match.team2_score
                total_rounds_against += match.team1_score
                if match.team2_score > match.team1_score:
                    wins += 1
        else:
            # Real match
            if match.team1 == team:
                total_rounds_for += match.team1_score
                total_rounds_against += match.team2_score
                if match.winner == team:
                    wins += 1
            else:
                total_rounds_for += match.team2_score
                total_rounds_against += match.team1_score
                if match.winner == team:
                    wins += 1

    total_matches = len(matches)
    win_rate = round((wins / total_matches) * 100, 1) if total_matches > 0 else 0
    avg_rounds_for = round(total_rounds_for / total_matches, 1) if total_matches > 0 else 0
    avg_rounds_against = round(total_rounds_against / total_matches, 1) if total_matches > 0 else 0

    return {
        'total_matches': total_matches,
        'wins': wins,
        'losses': total_matches - wins,
        'win_rate': win_rate,
        'avg_rounds_for': avg_rounds_for,
        'avg_rounds_against': avg_rounds_against,
        'round_diff': round(avg_rounds_for - avg_rounds_against, 1),
    }


# Existing views
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

        # If no real data exists, return empty queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weapon_choices'] = WeaponStats.WEAPON_CHOICES
        context['current_weapon'] = self.request.GET.get('weapon', 'all')

        # Check if we have real weapon stats
        real_weapon_stats = WeaponStats.objects.exists()

        if not real_weapon_stats:
            context['weapon_stats'] = self.generate_mock_weapon_stats()
            context['top_weapons'] = self.generate_mock_popular_weapons()
        else:
            context['top_weapons'] = WeaponStats.objects.values('weapon').annotate(
                total=Sum('total_kills')
            ).order_by('-total')[:5]

        return context

    def generate_mock_popular_weapons(self):
        return [
            {'weapon': 'ak47', 'total': 10165},
            {'weapon': 'm4a1s', 'total': 8547},
            {'weapon': 'awp', 'total': 4523},
            {'weapon': 'm4a4', 'total': 7212},
            {'weapon': 'deagle', 'total': 3876},
        ]

    def generate_mock_weapon_stats(self):
        # Get some real players to use in our mock data
        players = list(User.objects.filter(is_active=True)[:20])

        if not players:
            return []

        mock_stats = []
        weapons = ['ak47', 'm4a1s', 'awp', 'm4a4', 'deagle', 'glock', 'usp']

        # Generate stats for top players with each weapon
        for i, player in enumerate(players[:15]):  # Top 15 weapon users
            # Each player gets 1-2 weapons they're "good" with
            player_weapons = random.sample(weapons, random.randint(1, 2))

            for weapon in player_weapons:
                # Generate realistic stats based on weapon type
                if weapon == 'ak47':
                    base_kills = random.randint(850, 1200)
                elif weapon == 'm4a1s':
                    base_kills = random.randint(750, 1100)
                elif weapon == 'awp':
                    base_kills = random.randint(400, 650)
                elif weapon == 'm4a4':
                    base_kills = random.randint(700, 1000)
                elif weapon == 'deagle':
                    base_kills = random.randint(300, 500)
                else:
                    base_kills = random.randint(200, 400)

                # Generate realistic accuracy and headshot stats
                total_shots = int(base_kills * random.uniform(3.5, 6.0))  # Realistic accuracy
                headshot_kills = int(base_kills * random.uniform(0.25, 0.55))  # HS percentage

                # Create mock stat object
                mock_stat = type('MockWeaponStat', (), {
                    'player': player,
                    'weapon': weapon,
                    'total_kills': base_kills,
                    'total_shots': total_shots,
                    'headshot_kills': headshot_kills,
                    'get_weapon_display': lambda: dict(WeaponStats.WEAPON_CHOICES)[weapon],
                    'headshot_percentage': round((headshot_kills / base_kills) * 100, 1),
                    'accuracy_percentage': round((base_kills / total_shots) * 100, 1),
                })

                mock_stats.append(mock_stat)

        # Sort by total kills and return top 50
        return sorted(mock_stats, key=lambda x: x.total_kills, reverse=True)[:50]


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

        # Check if we have real map stats
        real_map_stats = MapStats.objects.exists()

        if not real_map_stats:
            context['map_stats'] = self.generate_mock_map_stats()

        # Always show popular maps
        context['popular_maps'] = self.generate_mock_popular_maps()

        return context

    def generate_mock_popular_maps(self):
        return [
            {'map_name': 'dust2', 'total_matches': 3420},
            {'map_name': 'mirage', 'total_matches': 3180},
            {'map_name': 'inferno', 'total_matches': 2950},
            {'map_name': 'cache', 'total_matches': 2780},
            {'map_name': 'overpass', 'total_matches': 2340},
            {'map_name': 'train', 'total_matches': 2120},
            {'map_name': 'cobblestone', 'total_matches': 1890}
        ]

    def generate_mock_map_stats(self):
        # Get some real players to use in our mock data
        players = list(User.objects.filter(is_active=True)[:25])

        if not players:
            return []

        mock_stats = []
        maps = ['dust2', 'mirage', 'inferno', 'cache', 'overpass', 'train', 'cobblestone']

        # Generate stats for players on different maps
        for i, player in enumerate(players):
            # Each player has stats on 2-4 maps (their preferred maps)
            player_maps = random.sample(maps, random.randint(2, 4))

            for map_name in player_maps:
                # Generate realistic match counts based on map popularity
                if map_name in ['dust2', 'mirage']:
                    matches_played = random.randint(45, 85)  # Popular maps
                elif map_name in ['inferno', 'cache']:
                    matches_played = random.randint(35, 65)  # Moderately popular
                else:
                    matches_played = random.randint(25, 55)  # Less popular

                # Generate realistic win rates (45-75%)
                win_rate = random.uniform(45, 75)
                matches_won = int(matches_played * (win_rate / 100))

                # Generate realistic K/D stats
                total_kills = int(matches_played * random.uniform(15, 25))  # 15-25 kills per match
                total_deaths = int(matches_played * random.uniform(12, 20))  # 12-20 deaths per match

                # Make sure deaths aren't zero
                if total_deaths == 0:
                    total_deaths = 1

                # Create mock stat object
                map_display_name = dict(MapStats.MAP_CHOICES)[map_name]
                mock_stat = type('MockMapStat', (), {
                    'player': player,
                    'map_name': map_name,
                    'matches_played': matches_played,
                    'matches_won': matches_won,
                    'total_kills': total_kills,
                    'total_deaths': total_deaths,
                    'get_map_name_display': lambda: map_display_name,
                    'win_rate': round(win_rate, 1),
                    'kd_ratio': round(total_kills / total_deaths, 2),
                })

                mock_stats.append(mock_stat)

        # Sort by matches played and return top 50
        return sorted(mock_stats, key=lambda x: x.matches_played, reverse=True)[:50]


def leaderboard(request):

    # Top players by total kills
    top_killers = User.objects.annotate(
        total_kills=Sum('match_stats__kills'),
        total_deaths=Sum('match_stats__deaths'),
        total_matches=Count('match_stats'),
        avg_kills=Avg('match_stats__kills')
    ).filter(
        total_kills__gt=0
    ).order_by('-total_kills')[:10]

    # Calculate K/D ratios for real players
    for player in top_killers:
        if player.total_deaths and player.total_deaths > 0:
            player.kd_ratio = round(player.total_kills / player.total_deaths, 2)
        else:
            player.kd_ratio = player.total_kills

    if len(top_killers) < 5:
        top_killers = generate_mock_top_fraggers()

    # Most active players
    most_active = User.objects.annotate(
        match_count=Count('match_stats')
    ).filter(match_count__gt=0).order_by('-match_count')[:10]

    # If not enough active players, generate mock ones
    if len(most_active) < 5:
        most_active = generate_mock_active_players()

    weapon_popularity = [
        {'weapon': 'ak47', 'total_kills': 10165, 'user_count': 245},
        {'weapon': 'm4a1s', 'total_kills': 8547, 'user_count': 198},
        {'weapon': 'awp', 'total_kills': 4523, 'user_count': 156},
        {'weapon': 'm4a4', 'total_kills': 7212, 'user_count': 187},
        {'weapon': 'deagle', 'total_kills': 3876, 'user_count': 134},
    ]

    # Mock map popularity
    map_popularity = [
        {'map_name': 'dust2', 'total_matches': 3420, 'user_count': 287},
        {'map_name': 'mirage', 'total_matches': 3180, 'user_count': 265},
        {'map_name': 'inferno', 'total_matches': 2950, 'user_count': 251},
        {'map_name': 'cache', 'total_matches': 2780, 'user_count': 234},
        {'map_name': 'overpass', 'total_matches': 2340, 'user_count': 198},
        {'map_name': 'train', 'total_matches': 2120, 'user_count': 187},
        {'map_name': 'cobblestone', 'total_matches': 1890, 'user_count': 156}
    ]

    # Top teams by activity
    top_teams = Team.objects.filter(is_active=True).annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('-founded_date')[:10]

    # Generate mock team activity if needed
    if len(top_teams) < 5:
        most_active_teams = generate_mock_active_teams()
    else:
        most_active_teams = top_teams

    context = {
        'top_killers': top_killers,
        'top_teams': top_teams,
        'most_active': most_active,
        'most_active_teams': most_active_teams,
        'weapon_popularity': weapon_popularity,
        'map_popularity': map_popularity,
        'total_players': User.objects.count(),
        'total_teams': Team.objects.filter(is_active=True).count(),
        'total_matches': max(PlayerMatchStats.objects.values('match').distinct().count(), 1247),
        # At least 1247 matches!
    }

    return render(request, 'stats/leaderboard.html', context)


def generate_mock_top_fraggers():
    fake_fraggers = [
        {'username': 'k1ngslayer_', 'total_kills': 2847, 'total_deaths': 1923, 'kd_ratio': 1.48,
         'rank': 'global_elite'},
        {'username': 'HEADSHOT_MACHINE', 'total_kills': 2654, 'total_deaths': 1876, 'kd_ratio': 1.42,
         'rank': 'global_elite'},
        {'username': 'AWP_BEAST_2024', 'total_kills': 2398, 'total_deaths': 1754, 'kd_ratio': 1.37, 'rank': 'supreme'},
        {'username': 'FragMaster_Pro', 'total_kills': 2156, 'total_deaths': 1634, 'kd_ratio': 1.32, 'rank': 'supreme'},
        {'username': 'NoScopeKing', 'total_kills': 1987, 'total_deaths': 1523, 'kd_ratio': 1.30,
         'rank': 'legendary_eagle'},
    ]

    mock_players = []
    for i, data in enumerate(fake_fraggers):
        rank_display = data['rank'].replace('_', ' ').title()
        mock_player = type('MockPlayer', (), {
            'id': f'mock_{i}',
            'username': data['username'],
            'total_kills': data['total_kills'],
            'total_deaths': data['total_deaths'],
            'kd_ratio': data['kd_ratio'],
            'rank': data['rank'],
            'avatar': None,
            'get_rank_display': lambda: rank_display,
        })
        mock_players.append(mock_player)

    return mock_players


def generate_mock_active_players():
    """Generate most active players with realistic match counts"""
    fake_active = [
        {'username': 'MatchAddict2024', 'match_count': 387, 'rank': 'global_elite'},
        {'username': 'GrindMaster_CS', 'match_count': 342, 'rank': 'supreme'},
        {'username': 'CompetitiveGod', 'match_count': 298, 'rank': 'supreme'},
        {'username': 'RankUpGrinder', 'match_count': 276, 'rank': 'legendary_eagle'},
        {'username': 'MatchMaking_Pro', 'match_count': 254, 'rank': 'legendary_eagle'},
    ]

    mock_players = []
    for i, data in enumerate(fake_active):
        rank_display = data['rank'].replace('_', ' ').title()
        mock_player = type('MockPlayer', (), {
            'id': f'active_mock_{i}',
            'username': data['username'],
            'match_count': data['match_count'],
            'rank': data['rank'],
            'avatar': None,
            'get_rank_display': lambda: rank_display,
        })
        mock_players.append(mock_player)

    return mock_players


def generate_mock_active_teams():
    """Generate most active teams with realistic match counts"""
    fake_teams = [
        {'name': 'Digital Dragons', 'tag': 'DD', 'matches': 384},
        {'name': 'Cyber Wolves', 'tag': 'CW', 'matches': 367},
        {'name': 'Elite Squad', 'tag': 'ES', 'matches': 341},
        {'name': 'Pro Gamers United', 'tag': 'PGU', 'matches': 298},
        {'name': 'Victory Legends', 'tag': 'VL', 'matches': 276},
    ]

    mock_teams = []
    for i, data in enumerate(fake_teams):
        mock_team = type('MockTeam', (), {
            'id': f'team_mock_{i}',
            'name': data['name'],
            'tag': data['tag'],
            'match_count': data['matches'],
            'member_count': random.randint(5, 8),
            'logo': None,
            'pk': f'mock_{i}',
        })
        mock_teams.append(mock_team)

    return mock_teams