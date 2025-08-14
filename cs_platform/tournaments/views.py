from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Tournament, TournamentParticipation
from .forms import TournamentCreateForm, TournamentRegistrationForm
from teams.models import Team


# Class-based view for tournament list
class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournaments/tournament_list.html'
    context_object_name = 'tournaments'
    paginate_by = 12
    ordering = ['-start_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', 'all')

        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('organizer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Tournament.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', 'all')
        return context


# Enhanced tournament detail view with admin capabilities
class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'tournaments/tournament_detail.html'
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tournament = self.object

        context['participants'] = tournament.participants.all().select_related('team').order_by('placement',
                                                                                                'registration_date')
        context['spots_left'] = tournament.max_teams - tournament.participants.count()
        context['can_register'] = (
                self.request.user.is_authenticated and
                tournament.status == 'upcoming' and
                timezone.now() < tournament.registration_deadline and
                context['spots_left'] > 0
        )

        # Check if user is tournament organizer (admin powers!)
        context['is_organizer'] = (
                self.request.user.is_authenticated and
                tournament.organizer == self.request.user
        )

        # If user is organizer, get ALL teams for admin panel
        if context['is_organizer']:
            # Get all teams that are NOT already in this tournament
            available_teams = Team.objects.filter(is_active=True).exclude(
                tournament_participations__tournament=tournament
            ).order_by('-is_professional', 'name')

            context['available_teams_for_admin'] = available_teams
            context['professional_teams'] = available_teams.filter(is_professional=True)
            context['community_teams'] = available_teams.filter(is_professional=False)

        # Check if user has teams that can register (normal registration)
        if self.request.user.is_authenticated and not context['is_organizer']:
            user_teams = Team.objects.filter(
                memberships__player=self.request.user,
                memberships__is_active=True,
                is_active=True
            ).exclude(
                tournament_participations__tournament=tournament
            ).distinct()
            context['available_teams'] = user_teams

        return context


# Class-based view for tournament creation
class TournamentCreateView(LoginRequiredMixin, CreateView):
    model = Tournament
    form_class = TournamentCreateForm
    template_name = 'tournaments/tournament_create.html'

    def form_valid(self, form):
        try:
            tournament = form.save(commit=False)
            tournament.organizer = self.request.user
            tournament.save()

            messages.success(self.request, f'Tournament "{tournament.name}" created successfully!')
            return redirect('tournament_detail', pk=tournament.pk)

        except Exception as e:
            messages.error(self.request, f'Error creating tournament: {str(e)}')
            return super().form_invalid(form)

    def get_success_url(self):
        return f'/tournaments/{self.object.pk}/'


# Function-based view for normal tournament registration
@login_required
def tournament_register(request, pk):
    """Register user's own team for tournament"""
    tournament = get_object_or_404(Tournament, pk=pk)

    # Check if tournament is open for registration
    if tournament.status != 'upcoming':
        messages.error(request, 'Registration is closed for this tournament!')
        return redirect('tournament_detail', pk=pk)

    if timezone.now() > tournament.registration_deadline:
        messages.error(request, 'Registration deadline has passed!')
        return redirect('tournament_detail', pk=pk)

    if tournament.participants.count() >= tournament.max_teams:
        messages.error(request, 'Tournament is full!')
        return redirect('tournament_detail', pk=pk)

    # Get user's available teams
    available_teams = Team.objects.filter(
        memberships__player=request.user,
        memberships__is_active=True,
        is_active=True
    ).exclude(
        tournament_participations__tournament=tournament
    ).distinct()

    if not available_teams.exists():
        messages.error(request, 'You have no available teams to register!')
        return redirect('tournament_detail', pk=pk)

    if request.method == 'POST':
        form = TournamentRegistrationForm(request.user, request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    team = form.cleaned_data['team']

                    # Check if team captain approves (if user is not captain)
                    if team.captain != request.user:
                        # For now, allow any team member to register
                        # In production, you might want captain approval
                        pass

                    TournamentParticipation.objects.create(
                        tournament=tournament,
                        team=team
                    )

                    messages.success(request, f'Team "{team.name}" registered for "{tournament.name}"!')
                    return redirect('tournament_detail', pk=pk)

            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = TournamentRegistrationForm(request.user)

    context = {
        'form': form,
        'tournament': tournament,
        'available_teams': available_teams,
    }
    return render(request, 'tournaments/tournament_register.html', context)


# NEW: Admin function to add ANY team to tournament
@login_required
@require_POST
def admin_add_team(request, tournament_pk):
    """Tournament organizer can add any team to their tournament"""
    tournament = get_object_or_404(Tournament, pk=tournament_pk)

    # Check if user is the organizer
    if tournament.organizer != request.user:
        messages.error(request, 'Only the tournament organizer can add teams!')
        return redirect('tournament_detail', pk=tournament_pk)

    team_id = request.POST.get('team_id')
    if not team_id:
        messages.error(request, 'No team selected!')
        return redirect('tournament_detail', pk=tournament_pk)

    try:
        team = get_object_or_404(Team, pk=team_id, is_active=True)

        # Check if tournament is full
        if tournament.participants.count() >= tournament.max_teams:
            messages.error(request, 'Tournament is full!')
            return redirect('tournament_detail', pk=tournament_pk)

        # Check if team is already registered
        if TournamentParticipation.objects.filter(tournament=tournament, team=team).exists():
            messages.warning(request, f'Team "{team.name}" is already registered!')
            return redirect('tournament_detail', pk=tournament_pk)

        # Add team to tournament
        with transaction.atomic():
            TournamentParticipation.objects.create(
                tournament=tournament,
                team=team
            )

            team_type = "Professional" if team.is_professional else "Community"
            messages.success(request, f'{team_type} team "{team.name}" added to tournament!')

    except Exception as e:
        messages.error(request, f'Error adding team: {str(e)}')

    return redirect('tournament_detail', pk=tournament_pk)


# NEW: Admin function to remove team from tournament
@login_required
@require_POST
def admin_remove_team(request, tournament_pk):
    """Tournament organizer can remove any team from their tournament"""
    tournament = get_object_or_404(Tournament, pk=tournament_pk)

    # Check if user is the organizer
    if tournament.organizer != request.user:
        messages.error(request, 'Only the tournament organizer can remove teams!')
        return redirect('tournament_detail', pk=tournament_pk)

    team_id = request.POST.get('team_id')
    if not team_id:
        messages.error(request, 'No team selected!')
        return redirect('tournament_detail', pk=tournament_pk)

    try:
        team = get_object_or_404(Team, pk=team_id)

        # Find and remove participation
        participation = TournamentParticipation.objects.filter(
            tournament=tournament,
            team=team
        ).first()

        if not participation:
            messages.warning(request, f'Team "{team.name}" is not registered in this tournament!')
            return redirect('tournament_detail', pk=tournament_pk)

        with transaction.atomic():
            participation.delete()

            team_type = "Professional" if team.is_professional else "Community"
            messages.success(request, f'{team_type} team "{team.name}" removed from tournament!')

    except Exception as e:
        messages.error(request, f'Error removing team: {str(e)}')

    return redirect('tournament_detail', pk=tournament_pk)


# NEW: AJAX endpoint to get team info
@login_required
def get_team_info(request, team_pk):
    """Get team information for admin panel preview"""
    try:
        team = get_object_or_404(Team, pk=team_pk, is_active=True)

        data = {
            'id': team.id,
            'name': team.name,
            'tag': team.tag,
            'is_professional': team.is_professional,
            'country': team.country,
            'flag': team.get_country_flag(),
            'member_count': team.memberships.filter(is_active=True).count(),
            'captain': team.captain.username if team.captain else 'No Captain',
            'logo_url': team.logo.url if team.logo else None,
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)