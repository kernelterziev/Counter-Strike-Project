from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
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


# Class-based view for tournament detail
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

        # Check if user has teams that can register
        if self.request.user.is_authenticated:
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


# Function-based view for tournament registration
@login_required
def tournament_register(request, pk):
    """Register team for tournament"""
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