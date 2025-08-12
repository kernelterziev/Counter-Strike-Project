from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db import transaction
from .models import Match, PlayerMatchStats
from .forms import MatchCreateForm, MatchResultForm, PlayerStatsForm
from teams.models import Team, TeamMembership


# Class-based view for match list
class MatchListView(ListView):
    model = Match
    template_name = 'matches/match_list.html'
    context_object_name = 'matches'
    paginate_by = 20
    ordering = ['-match_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        map_filter = self.request.GET.get('map')
        team_filter = self.request.GET.get('team')

        if map_filter:
            queryset = queryset.filter(map_name=map_filter)
        if team_filter:
            queryset = queryset.filter(
                models.Q(team1__name__icontains=team_filter) |
                models.Q(team2__name__icontains=team_filter)
            )

        return queryset.select_related('team1', 'team2')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['map_choices'] = Match.MAP_CHOICES
        return context


# Class-based view for match detail
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
        return context


# Class-based view for match creation
class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchCreateForm
    template_name = 'matches/match_create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Only show teams where user is a member
        user_teams = Team.objects.filter(
            memberships__player=self.request.user,
            memberships__is_active=True,
            is_active=True
        ).distinct()

        if user_teams.exists():
            # Set team1 to user's first team
            form.instance.team1 = user_teams.first()
            # Only allow selection of other teams for team2
            form.fields['team2'].queryset = Team.objects.filter(is_active=True).exclude(
                id__in=user_teams.values_list('id', flat=True)
            )
        else:
            messages.error(self.request, 'You need to be a member of a team to create matches!')

        return form

    def form_valid(self, form):
        try:
            user_teams = Team.objects.filter(
                memberships__player=self.request.user,
                memberships__is_active=True
            )

            if not user_teams.exists():
                messages.error(self.request, 'You must be a member of a team to create matches!')
                return redirect('team_list')

            match = form.save(commit=False)
            match.team1 = user_teams.first()
            match.save()

            messages.success(self.request, f'Match created: {match.team1.name} vs {match.team2.name}!')
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
                    return redirect('match_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error submitting result: {str(e)}')
    else:
        form = MatchResultForm(instance=match)

    context = {
        'form': form,
        'match': match,
    }
    return render(request, 'matches/match_result.html', context)