from django.urls import path
from . import views

urlpatterns = [
    path('weapons/', views.WeaponStatsView.as_view(), name='weapon_stats'),
    path('maps/', views.MapStatsView.as_view(), name='map_stats'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]