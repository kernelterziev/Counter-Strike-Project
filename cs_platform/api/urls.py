from django.urls import path
from . import views

urlpatterns = [
    # API Overview
    path('', views.api_overview, name='api_overview'),

    # Players
    path('players/', views.PlayerListView.as_view(), name='api_player_list'),
    path('players/<int:pk>/', views.PlayerDetailView.as_view(), name='api_player_detail'),

    # Teams
    path('teams/', views.TeamListView.as_view(), name='api_team_list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='api_team_detail'),

    # Matches
    path('matches/', views.MatchListView.as_view(), name='api_match_list'),
    path('matches/<int:pk>/', views.MatchDetailView.as_view(), name='api_match_detail'),

    # Tournaments
    path('tournaments/', views.TournamentListView.as_view(), name='api_tournament_list'),
    path('tournaments/<int:pk>/', views.TournamentDetailView.as_view(), name='api_tournament_detail'),

    # Stats
    path('weapon-stats/', views.WeaponStatsListView.as_view(), name='api_weapon_stats'),
]