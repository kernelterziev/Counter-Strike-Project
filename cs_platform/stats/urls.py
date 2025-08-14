from django.urls import path
from . import views, async_views

urlpatterns = [
    path('weapons/', views.WeaponStatsView.as_view(), name='weapon_stats'),
    path('maps/', views.MapStatsView.as_view(), name='map_stats'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),


    # Async views
    path('async/dashboard/', async_views.async_dashboard, name='async_dashboard'),
    path('async/leaderboard-data/', async_views.async_leaderboard_data, name='async_leaderboard_data'),
    path('async/player/<int:player_id>/', async_views.async_player_stats, name='async_player_stats'),
    path('async/team/<int:team_id>/', async_views.async_team_performance, name='async_team_performance'),
    path('player-comparison/', views.player_comparison, name='player_comparison'),
    path('team-history/<int:team_id>/', views.team_match_history, name='team_match_history'),
]