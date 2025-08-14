from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Avg, Count, Sum
import random
import hashlib
from .models import Match, PlayerMatchStats
from .forms import MatchCreateForm, MatchResultForm, PlayerStatsForm
from teams.models import Team, TeamMembership
from django.http import JsonResponse

def generate_match_prediction(team1, team2, map_name):
    """Generate realistic match prediction with betting odds"""

    # Create consistent seed for same matchup
    matchup_seed = int(hashlib.md5(f"{team1.id}_{team2.id}_{map_name}".encode()).hexdigest()[:8], 16)
    random.seed(matchup_seed)

    # Base probability calculation
    team1_strength = calculate_team_strength(team1, map_name)
    team2_strength = calculate_team_strength(team2, map_name)

    # Calculate win probabilities
    total_strength = team1_strength + team2_strength
    team1_win_prob = team1_strength / total_strength
    team2_win_prob = team2_strength / total_strength

    # Add some randomness for excitement (±10%)
    randomness = random.uniform(-0.1, 0.1)
    team1_win_prob += randomness
    team2_win_prob -= randomness

    # Ensure probabilities are within reasonable bounds
    team1_win_prob = max(0.15, min(0.85, team1_win_prob))
    team2_win_prob = 1.0 - team1_win_prob

    # Calculate betting odds (European format)
    team1_odds = round(1.0 / team1_win_prob, 2)
    team2_odds = round(1.0 / team2_win_prob, 2)

    # Generate score prediction
    predicted_score = generate_score_prediction(team1_win_prob)

    # Generate confidence level
    confidence = calculate_prediction_confidence(team1, team2)

    return {
        'team1_win_probability': round(team1_win_prob * 100, 1),
        'team2_win_probability': round(team2_win_prob * 100, 1),
        'team1_odds': team1_odds,
        'team2_odds': team2_odds,
        'predicted_winner': team1 if team1_win_prob > 0.5 else team2,
        'predicted_score': predicted_score,
        'confidence': confidence,
        'analysis': generate_match_analysis(team1, team2, map_name, team1_win_prob)
    }


def calculate_team_strength(team, map_name):
    """Calculate team strength based on various factors"""
    base_strength = 50  # Base strength for all teams

    # Professional team bonus
    if team.is_professional:
        base_strength += 25

        # World ranking bonus (lower ranking = higher strength)
        if team.world_ranking:
            ranking_bonus = max(0, 50 - team.world_ranking)
            base_strength += ranking_bonus

        # Prize money factor (more successful = stronger)
        if team.prize_money:
            prize_bonus = min(20, team.prize_money / 10000)  # Max 20 points
            base_strength += prize_bonus

    # Map-specific bonuses (some teams are better on certain maps)
    map_bonuses = {
        'dust2': [1, 3, 7, 2, 5],  # Different teams get different bonuses
        'mirage': [5, 1, 2, 8, 3],
        'inferno': [3, 7, 1, 4, 6],
        'cache': [2, 5, 9, 1, 4],
        'overpass': [8, 2, 4, 6, 1],
        'train': [4, 6, 3, 9, 2],
        'cobblestone': [6, 4, 8, 3, 7]
    }

    if map_name in map_bonuses:
        # Use team ID to get consistent map bonus
        bonus_index = team.id % len(map_bonuses[map_name])
        map_bonus = map_bonuses[map_name][bonus_index]
        base_strength += map_bonus

    # Team activity bonus (teams with more members are more active)
    member_count = team.memberships.filter(is_active=True).count()
    activity_bonus = min(10, member_count * 2)  # Max 10 points
    base_strength += activity_bonus

    # Add some team-specific randomness for variety
    team_seed = team.id * 12345
    random.seed(team_seed)
    team_variation = random.uniform(-5, 5)
    base_strength += team_variation

    return max(20, base_strength)  # Minimum strength of 20


def generate_score_prediction(team1_win_prob):
    """Generate realistic score prediction"""
    if team1_win_prob > 0.7:
        # Strong favorite
        return random.choice(['16-8', '16-10', '16-9', '16-7'])
    elif team1_win_prob > 0.6:
        # Moderate favorite
        return random.choice(['16-12', '16-13', '16-11', '16-14'])
    elif team1_win_prob > 0.4:
        # Close match
        return random.choice(['16-14', '19-17', '16-13', '22-20'])
    else:
        # Underdog predicted to win
        return random.choice(['8-16', '10-16', '12-16', '11-16'])


def calculate_prediction_confidence(team1, team2):
    """Calculate confidence level of the prediction"""

    # Higher confidence for matchups between similar level teams
    if team1.is_professional == team2.is_professional:
        base_confidence = 75
    else:
        base_confidence = 85  # More confident when pro vs amateur

    # Add some randomness
    confidence_variation = random.uniform(-10, 15)
    final_confidence = base_confidence + confidence_variation

    return round(max(60, min(95, final_confidence)), 1)


def generate_match_analysis(team1, team2, map_name, team1_win_prob):
    """Generate detailed match analysis"""

    analyses = []

    # Team type analysis
    if team1.is_professional and not team2.is_professional:
        analyses.append(f"{team1.name}'s professional experience gives them a significant edge")
    elif team2.is_professional and not team1.is_professional:
        analyses.append(f"{team2.name}'s professional status makes them heavy favorites")
    else:
        analyses.append("Both teams are evenly matched in terms of experience level")

    # Map analysis
    map_comments = {
        'dust2': "Classic map that favors AWP-heavy strategies",
        'mirage': "Balanced map that rewards tactical coordination",
        'inferno': "Close-quarters combat favors aggressive playstyles",
        'cache': "Mid control will be crucial for map dominance",
        'overpass': "Verticality and timing are key factors",
        'train': "Strong CT sides typically dominate this map",
        'cobblestone': "Long-range duels and positioning matter most"
    }

    if map_name in map_comments:
        analyses.append(map_comments[map_name])

    # Prediction confidence
    if team1_win_prob > 0.65:
        analyses.append(f"{team1.name} has strong momentum going into this match")
    elif team1_win_prob < 0.35:
        analyses.append(f"{team2.name} looks unstoppable in recent form")
    else:
        analyses.append("This match could go either way - expect a nail-biter!")

    return analyses


# Enhanced match list view
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'
    paginate_by = 20
    ordering = ['-match_date']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('team1', 'team2')

        # 🔍 SEARCH FUNCTIONALITY (instead of filter)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(team1__name__icontains=search_query) |
                Q(team2__name__icontains=search_query) |
                Q(team1__tag__icontains=search_query) |
                Q(team2__tag__icontains=search_query) |
                Q(map_name__icontains=search_query)
            )

        # Keep the existing filters but make them optional
        map_filter = self.request.GET.get('map')
        if map_filter and map_filter != 'all':
            queryset = queryset.filter(map_name=map_filter)

        match_type = self.request.GET.get('type')
        if match_type and match_type != 'all':
            queryset = queryset.filter(match_type=match_type)

        status_filter = self.request.GET.get('status')
        if status_filter == 'finished':
            queryset = queryset.filter(is_finished=True)
        elif status_filter == 'ongoing':
            queryset = queryset.filter(is_finished=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pass current search/filter values to template
        context['current_search'] = self.request.GET.get('search', '')
        context['current_map'] = self.request.GET.get('map', 'all')
        context['current_type'] = self.request.GET.get('type', 'all')
        context['current_status'] = self.request.GET.get('status', 'all')

        # Map and type choices for dropdowns
        context['map_choices'] = Match.MAP_CHOICES
        context['type_choices'] = Match.MATCH_TYPE_CHOICES if hasattr(Match, 'MATCH_TYPE_CHOICES') else []

        # Match statistics for dashboard feel
        context['total_matches'] = Match.objects.count()
        context['finished_matches'] = Match.objects.filter(is_finished=True).count()
        context['ongoing_matches'] = Match.objects.filter(is_finished=False).count()

        return context


# Enhanced match detail view with predictions
class MatchDetailView(DetailView):
    model = Match
    template_name = 'matches/match_detail.html'
    context_object_name = 'match'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = self.object

        context['player_stats'] = match.player_stats.all().select_related('player', 'team')
        context['team1_stats'] = match.player_stats.filter(team=match.team1)
        context['team2_stats'] = match.player_stats.filter(team=match.team2)

        # Generate match prediction if match hasn't started
        if not match.is_finished and match.team1_score == 0 and match.team2_score == 0:
            context['prediction'] = generate_match_prediction(
                match.team1,
                match.team2,
                match.map_name
            )

        return context


# Enhanced match creation view
class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchCreateForm
    template_name = 'matches/match_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            match = form.save()

            # Generate prediction for the new match
            prediction = generate_match_prediction(
                match.team1,
                match.team2,
                match.map_name
            )

            messages.success(
                self.request,
                f'Match created: {match.team1.name} vs {match.team2.name}! '
                f'AI predicts {prediction["predicted_winner"].name} to win with '
                f'{prediction["team1_win_probability" if prediction["predicted_winner"] == match.team1 else "team2_win_probability"]}% probability!'
            )
            return redirect('match_detail', pk=match.pk)

        except Exception as e:
            messages.error(self.request, f'Error creating match: {str(e)}')
            return super().form_invalid(form)


# Function-based view for match result submission
@login_required
def match_result(request, pk):
    """Submit match results - team captains only"""
    match = get_object_or_404(Match, pk=pk)

    # Check if user is captain of either team
    user_teams = Team.objects.filter(captain=request.user)
    if not (match.team1 in user_teams or match.team2 in user_teams):
        messages.error(request, 'Only team captains can submit match results!')
        return redirect('match_detail', pk=pk)

    if match.is_finished:
        messages.warning(request, 'This match is already finished!')
        return redirect('match_detail', pk=pk)

    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match)
        if form.is_valid():
            try:
                with transaction.atomic():
                    match = form.save()
                    messages.success(request, 'Match result submitted successfully!')
                    return redirect('match_detail', pk=match.pk)
            except Exception as e:
                messages.error(request, f'Error submitting result: {str(e)}')
    else:
        form = MatchResultForm(instance=match)

    context = {
        'form': form,
        'match': match,
    }
    return render(request, 'matches/match_result.html', context)



def delete_match(request, match_id):
    """Delete a match - BEAST MODE! 🔥"""
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        match_name = f"{match.team1.name} vs {match.team2.name}"
        match.delete()

        messages.success(request, f'🗑️ Match "{match_name}" has been deleted successfully!')
        return redirect('match_list')

    # If GET request, show confirmation page
    context = {
        'match': match,
        'title': 'Delete Match'
    }
    return render(request, 'matches/delete_match_confirm.html', context)


@user_passes_test(lambda u: u.is_staff)
def ajax_delete_match(request, match_id):
    """AJAX delete for smooth UX"""
    if request.method == 'POST':
        match = get_object_or_404(Match, id=match_id)
        match_name = f"{match.team1.name} vs {match.team2.name}"
        match.delete()

        return JsonResponse({
            'success': True,
            'message': f'Match "{match_name}" deleted successfully!',
            'redirect_url': '/matches/'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def match_stats_summary(request):
    """Quick stats for the match list page"""
    from django.db.models import Count

    stats = {
        'total_matches': Match.objects.count(),
        'finished_matches': Match.objects.filter(is_finished=True).count(),
        'ongoing_matches': Match.objects.filter(is_finished=False).count(),
        'popular_maps': Match.objects.values('map_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
    }

    return JsonResponse(stats)