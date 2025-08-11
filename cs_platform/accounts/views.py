from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, UserProfileForm

User = get_user_model()


#Function-based view for home page
def home(request):
    """Landing page accessible to everyone"""
    context = {
        'total_users': User.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'accounts/home.html', context)


#Function-based view for registration
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


#Class-based view for player list
class PlayerListView(ListView):
    model = User
    template_name = 'accounts/player_list.html'
    context_object_name = 'players'
    paginate_by = 20
    ordering = ['-date_joined']


#Class-based view for player detail
class PlayerDetailView(DetailView):
    model = User
    template_name = 'accounts/player_detail.html'
    context_object_name = 'player'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player = self.object
        context['recent_matches'] = player.match_stats.select_related('match')[:5]
        context['weapon_stats'] = player.weapon_stats.all()[:5]
        return context


#Class-based view for profile update
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_update.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return f'/accounts/player/{self.request.user.id}/'

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


#Function-based view for player search
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