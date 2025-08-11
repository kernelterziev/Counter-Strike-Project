from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.db import transaction
from .models import Team, TeamMembership
from .forms import TeamCreateForm, TeamJoinForm


# Class-based view for team list
class TeamListView(ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'
    paginate_by = 12
    queryset = Team.objects.filter(is_active=True)


# Class-based view for team detail
class TeamDetailView(DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        context['members'] = team.memberships.filter(is_active=True).select_related('player')
        context['recent_matches'] = team.matches_as_team1.union(team.matches_as_team2.all())[:5]
        return context


# Class-based view for team creation
class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamCreateForm
    template_name = 'teams/team_create.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                team = form.save(commit=False)
                team.captain = self.request.user
                team.save()

                # Add creator as first member
                TeamMembership.objects.create(
                    team=team,
                    player=self.request.user,
                    role='igl'
                )

                messages.success(self.request, f'Team "{team.name}" created successfully!')
                return redirect('team_detail', pk=team.pk)
        except Exception as e:
            messages.error(self.request, f'Error creating team: {str(e)}')
            return super().form_invalid(form)


# Class-based view for team update
class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamCreateForm
    template_name = 'teams/team_update.html'

    def get_queryset(self):
        return Team.objects.filter(captain=self.request.user)

    def get_success_url(self):
        return f'/teams/{self.object.pk}/'


# Function-based view for team roster
@login_required
def team_roster(request, pk):
    """Manage team roster - captain only"""
    team = get_object_or_404(Team, pk=pk, captain=request.user)
    members = team.memberships.filter(is_active=True).select_related('player')

    context = {
        'team': team,
        'members': members,
    }
    return render(request, 'teams/team_roster.html', context)


# Function-based view for joining team
@login_required
def join_team(request, pk):
    """Join a team"""
    team = get_object_or_404(Team, pk=pk, is_active=True)

    # Check if user is already in team
    if TeamMembership.objects.filter(player=request.user, team=team, is_active=True).exists():
        messages.warning(request, 'You are already a member of this team!')
        return redirect('team_detail', pk=pk)

    if request.method == 'POST':
        form = TeamJoinForm(request.POST)
        if form.is_valid():
            try:
                membership = form.save(commit=False)
                membership.team = team
                membership.player = request.user
                membership.save()
                messages.success(request, f'Successfully joined {team.name}!')
                return redirect('team_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error joining team: {str(e)}')
    else:
        form = TeamJoinForm()

    context = {'form': form, 'team': team}
    return render(request, 'teams/join_team.html', context)