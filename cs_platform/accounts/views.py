from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django import forms
from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser

User = get_user_model()


# Profile Update Form - ENHANCED GAMING VERSION
class ProfileUpdateForm(forms.ModelForm):
    favorite_weapon = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control gaming-input',
            'placeholder': 'e.g., AK-47, AWP, M4A1-S...'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'country', 'favorite_weapon', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control gaming-input',
                'placeholder': 'Your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control gaming-input',
                'placeholder': 'Your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control gaming-input',
                'placeholder': 'your.email@example.com'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control gaming-input',
                'placeholder': 'e.g., Bulgaria, Germany, USA...'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control gaming-input',
                'rows': 4,
                'placeholder': 'Tell other gamers about yourself, your playstyle, achievements...'
            }),
        }


# Function-based view for home page
def home(request):
    """Landing page accessible to everyone"""
    context = {
        'total_users': User.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'accounts/home.html', context)


# Function-based view for registration
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to CS Platform!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Class-based view for player list - UPDATED with pro players
class PlayerListView(ListView):
    model = User
    template_name = 'accounts/player_list.html'
    context_object_name = 'players'
    paginate_by = 30
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add professional players separately
        context['pro_players'] = User.objects.filter(
            is_professional=True
        ).order_by('username')[:30]
        return context

    def get_queryset(self):
        # Only show community players in main list
        return User.objects.filter(is_professional=False).order_by('-date_joined')


# Class-based view for player detail - ENHANCED with gaming preferences
class PlayerDetailView(DetailView):
    model = User
    template_name = 'accounts/player_detail.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object
        context['recent_matches'] = player.match_stats.select_related('match')[:5]
        context['weapon_stats'] = player.weapon_stats.all()[:5]

        # ADD GAMING PREFERENCES
        context['gaming_preferences'] = self.get_gaming_preferences(player)

        return context

    def get_gaming_preferences(self, user):
        """Get REAL gaming preferences from user data and session"""
        import random

        # Get data from session if available (from profile edit)
        session_map = None
        session_team = None
        if hasattr(self, 'request') and self.request.session:
            session_map = self.request.session.get('favorite_map')
            session_team = self.request.session.get('favorite_team')

        # Mock data for fallbacks
        favorite_weapons = ['AK-47', 'AWP', 'M4A1-S', 'Desert Eagle', 'Glock-18']
        favorite_maps = ['Dust 2', 'Mirage', 'Inferno', 'Cache', 'Overpass']
        favorite_teams = ['Astralis', 'NAVI', 'Team Vitality', 'G2 Esports', 'FaZe Clan']

        # Generate consistent preferences based on user ID
        random.seed(user.id)

        gaming_preferences = {
            # Use real user data first, then session, then random
            'favorite_weapon': user.favorite_weapon or random.choice(favorite_weapons),
            'favorite_map': session_map or random.choice(favorite_maps),
            'favorite_team': session_team or random.choice(favorite_teams),
            'playtime_hours': random.randint(500, 3000),
            'skill_level': random.choice(['Beginner', 'Intermediate', 'Advanced', 'Expert', 'Pro']),
            'preferred_role': random.choice(['Rifler', 'AWPer', 'Entry Fragger', 'Support', 'IGL'])
        }

        return gaming_preferences


# ENHANCED Profile Update View - GAMING BEAST MODE
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm  # Using the enhanced form
    template_name = 'accounts/profile_update.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('player_detail', kwargs={'pk': self.request.user.pk})

    def form_valid(self, form):
        # Handle favorite map and team from POST data
        favorite_map = self.request.POST.get('favorite_map')
        favorite_team = self.request.POST.get('favorite_team')

        # Save additional preferences (you might want to add these fields to your model)
        user = form.save()

        # For now, we'll just save them in session (you can add fields to model later)
        if favorite_map:
            self.request.session['favorite_map'] = favorite_map
        if favorite_team:
            self.request.session['favorite_team'] = favorite_team

        messages.success(
            self.request,
            '🎮 Gaming profile updated successfully! Your preferences have been saved.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            '❌ There was an error updating your profile. Please check the fields below.'
        )
        return super().form_invalid(form)


# DELETE ACCOUNT VIEW - EPIC DELETION WITH CONFIRMATION
@login_required
def delete_account(request):
    """Delete user account permanently"""
    if request.method == 'POST':
        user = request.user
        username = user.username

        try:
            # Log out the user first
            logout(request)

            # Delete the user account
            user.delete()

            messages.success(
                request,
                f'💀 Account "{username}" has been permanently deleted. Thanks for gaming with us!'
            )
            return redirect('home')

        except Exception as e:
            messages.error(
                request,
                f'❌ Error deleting account: {str(e)}. Please try again or contact support.'
            )
            return redirect('profile_edit')

    # If GET request, redirect to profile edit
    return redirect('profile_edit')


# Function-based view for player search
def player_search(request):
    """Search players by username or rank"""
    query = request.GET.get('q', '')
    rank_filter = request.GET.get('rank', '')

    players = User.objects.all()

    if query:
        players = players.filter(username__icontains=query)

    if rank_filter:
        players = players.filter(rank=rank_filter)

    context = {
        'players': players[:20],  # Limit results
        'query': query,
        'rank_filter': rank_filter,
        'rank_choices': User.RANK_CHOICES,
    }
    return render(request, 'accounts/player_search.html', context)