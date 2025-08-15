from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import random
import hashlib
from .models import Team, TeamMembership
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def create_team_with_roster(request):
    """Create team with 5 players and roles - BEAST MODE! 🔥"""

    if request.method == 'POST':
        # Get form data
        team_name = request.POST.get('team_name')
        team_tag = request.POST.get('team_tag')
        team_type = request.POST.get('team_type')
        country = request.POST.get('country')

        # Get player positions
        captain_id = request.POST.get('captain')
        awper_id = request.POST.get('awper')
        entry_fragger_id = request.POST.get('entry_fragger')
        support_id = request.POST.get('support')
        rifler_id = request.POST.get('rifler')

        # Validation
        player_ids = [captain_id, awper_id, entry_fragger_id, support_id, rifler_id]

        # Check for empty positions
        if not all(player_ids):
            messages.error(request, '❌ All 5 positions must be filled!')
            return render(request, 'teams/create_team_roster.html', {
                'players': User.objects.all().order_by('username'),
            })

        # Check for duplicate players
        if len(set(player_ids)) != 5:
            messages.error(request, '❌ Cannot select the same player for multiple positions!')
            return render(request, 'teams/create_team_roster.html', {
                'players': User.objects.all().order_by('username'),
            })

        # Check if team name already exists
        if Team.objects.filter(name=team_name).exists():
            messages.error(request, f'❌ Team name "{team_name}" already exists!')
            return render(request, 'teams/create_team_roster.html', {
                'players': User.objects.all().order_by('username'),
            })

        # Check if tag already exists
        if Team.objects.filter(tag=team_tag).exists():
            messages.error(request, f'❌ Team tag "{team_tag}" already exists!')
            return render(request, 'teams/create_team_roster.html', {
                'players': User.objects.all().order_by('username'),
            })

        try:
            # Create the team
            team = Team.objects.create(
                name=team_name,
                tag=team_tag,
                country=country if country else None,
                is_professional=(team_type == 'professional'),
                captain_id=captain_id,  # Set the captain
                founded_date=timezone.now().date()
            )

            # Define roles mapping
            roles_mapping = {
                captain_id: 'captain',
                awper_id: 'awper',
                entry_fragger_id: 'entry_fragger',
                support_id: 'support',
                rifler_id: 'rifler'
            }

            # Add all players to team with their roles
            for player_id in player_ids:
                player = User.objects.get(id=player_id)
                role = roles_mapping[player_id]

                TeamMembership.objects.create(
                    team=team,
                    player=player,
                    role=role,
                    is_active=True,
                    joined_date=timezone.now().date()
                )

            # Success message with team info
            player_names = [User.objects.get(id=pid).username for pid in player_ids]
            messages.success(
                request,
                f'🏆 Team "{team_name}" created successfully with roster: {", ".join(player_names)}'
            )

            return redirect('team_detail', pk=team.pk)

        except Exception as e:
            messages.error(request, f'❌ Error creating team: {str(e)}')
            return render(request, 'teams/create_team_roster.html', {
                'players': User.objects.all().order_by('username'),
            })

    # GET request - show the form
    context = {
        'players': User.objects.filter(is_active=True).order_by('username'),
        'title': 'Create Team with Roster'
    }

    return render(request, 'teams/create_team_roster.html', context)


# 🎯 BONUS: Quick team stats after creation
def team_roster_preview(request, team_id):
    """Preview team roster with roles"""
    team = get_object_or_404(Team, id=team_id)

    # Get team members with roles
    roster = TeamMembership.objects.filter(
        team=team,
        is_active=True
    ).select_related('player').order_by('role')

    # Role display mapping
    role_display = {
        'captain': '👑 Captain/IGL',
        'awper': '🎯 AWPer',
        'entry_fragger': '⚡ Entry Fragger',
        'support': '🛡️ Support',
        'rifler': '🔫 Rifler'
    }

    # Add display names to roster
    for member in roster:
        member.role_display = role_display.get(member.role, member.role.title())

    context = {
        'team': team,
        'roster': roster,
        'title': f'{team.name} Roster'
    }

    return render(request, 'teams/roster_preview.html', context)

def generate_team_match_history(team):
    """Generate realistic match history for team detail page"""
    # Use team ID for consistent results
    team_seed = int(hashlib.md5(str(team.id).encode()).hexdigest()[:8], 16)
    random.seed(team_seed)

    # Realistic opponent teams based on team level
    if team.is_professional:
        opponent_pools = [
            'Team Vitality', 'NAVI', 'G2 Esports', 'FaZe Clan', 'MOUZ',
            'BIG', 'Team Spirit', 'Cloud9', 'FURIA', 'Heroic',
            'ENCE', 'OG', 'Ninjas in Pyjamas', 'Complexity', 'Eternal Fire'
        ]
    else:
        opponent_pools = [
            'Team Alpha', 'Beta Squad', 'Gamma Force', 'Delta Warriors',
            'Epsilon Gaming', 'Zeta Esports', 'Theta Team', 'Sigma Squad',
            'Phoenix Rising', 'Storm Riders', 'Shadow Hawks', 'Lightning Bolts'
        ]

    maps = ['Mirage', 'Dust 2', 'Inferno', 'Cache', 'Overpass', 'Train', 'Nuke']

    match_history = []

    for i in range(5):  # Last 5 matches
        # Create realistic match dates
        days_ago = (i + 1) * random.randint(2, 5)  # 2-25 days ago
        match_date = timezone.now() - timedelta(days=days_ago)

        opponent_name = random.choice(opponent_pools)

        # Generate realistic series (BO1, BO3, or BO5)
        series_types = ['bo1', 'bo3', 'bo3', 'bo5'] if team.is_professional else ['bo1', 'bo1', 'bo3']
        series_type = random.choice(series_types)

        if series_type == 'bo1':
            num_maps = 1
            maps_to_win = 1
        elif series_type == 'bo3':
            num_maps = random.choice([2, 3])  # Can end 2-0 or go to 3rd map
            maps_to_win = 2
        else:  # bo5
            num_maps = random.choice([3, 4, 5])
            maps_to_win = 3

        # Generate map results
        selected_maps = random.sample(maps, num_maps)
        map_results = []
        team_maps_won = 0
        opponent_maps_won = 0

        for j, map_name in enumerate(selected_maps):
            # Generate realistic scores
            if team.is_professional:
                # Pro teams have closer matches
                team_score = random.randint(13, 19)
                opponent_score = random.randint(13, 19)
            else:
                # Community matches can be more varied
                team_score = random.randint(10, 16)
                opponent_score = random.randint(8, 16)

            # Ensure one team wins
            if team_score == opponent_score:
                if random.choice([True, False]):
                    team_score += random.randint(1, 3)
                else:
                    opponent_score += random.randint(1, 3)

            # Track series score
            if team_score > opponent_score:
                team_maps_won += 1
                map_winner = 'team'
            else:
                opponent_maps_won += 1
                map_winner = 'opponent'

            map_results.append({
                'map': map_name,
                'team_score': team_score,
                'opponent_score': opponent_score,
                'winner': map_winner
            })

            # Check if series is over
            if team_maps_won == maps_to_win or opponent_maps_won == maps_to_win:
                break

        # Determine series winner
        series_winner = 'team' if team_maps_won > opponent_maps_won else 'opponent'

        match_history.append({
            'opponent': opponent_name,
            'opponent_tag': f'[{opponent_name[:3].upper()}]',
            'date': match_date,
            'series_score': f"{team_maps_won}-{opponent_maps_won}",
            'series_winner': series_winner,
            'series_type': series_type.upper(),
            'map_results': map_results,
            'total_maps': len(map_results)
        })

    return match_history


class TeamListView(ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_queryset(self):
        queryset = Team.objects.filter(is_active=True).annotate(
            member_count=Count('memberships', filter=Q(memberships__is_active=True))
        )

        # Filter by professional status
        pro_filter = self.request.GET.get('professional')
        if pro_filter == 'true':
            queryset = queryset.filter(is_professional=True)
        elif pro_filter == 'false':
            queryset = queryset.filter(is_professional=False)

        # Filter by country
        country_filter = self.request.GET.get('country')
        if country_filter:
            queryset = queryset.filter(country__icontains=country_filter)

        # Search by name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(tag__icontains=search)
            )

        return queryset.order_by('-is_professional', '-founded_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['professional_teams'] = Team.objects.filter(is_professional=True, is_active=True).count()
        context['community_teams'] = Team.objects.filter(is_professional=False, is_active=True).count()
        return context


class TeamDetailView(DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object

        # Get team members
        context['members'] = team.memberships.filter(is_active=True).select_related('player')
        context['member_count'] = context['members'].count()

        # Check if user can join team
        if self.request.user.is_authenticated:
            context['user_is_member'] = team.memberships.filter(
                player=self.request.user, is_active=True
            ).exists()
            context['user_is_captain'] = team.captain == self.request.user
        else:
            context['user_is_member'] = False
            context['user_is_captain'] = False

        # Generate match history only for older teams (created more than 1 day ago)
        if (timezone.now().date() - team.founded_date).days > 0:
            context['match_history'] = generate_team_match_history(team)
        else:
            context['match_history'] = []  # New team, no matches yet

        # Calculate team performance stats
        match_history = context['match_history']
        if match_history:
            wins = sum(1 for match in match_history if match['series_winner'] == 'team')
            total_matches = len(match_history)

            context['team_performance'] = {
                'recent_matches': total_matches,
                'wins': wins,
                'losses': total_matches - wins,
                'win_rate': round((wins / total_matches) * 100, 1) if total_matches > 0 else 0
            }
        else:
            context['team_performance'] = {
                'recent_matches': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0
            }

        return context


def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.method == 'POST':
        team_name = f"[{team.tag}] {team.name}"
        team.delete()

        messages.success(request, f'🗑️ Team "{team_name}" has been deleted successfully!')
        return redirect('team_list')

    # If GET request, show confirmation page
    context = {
        'team': team,
        'title': 'Delete Team'
    }
    return render(request, 'teams/delete_team_confirm.html', context)
