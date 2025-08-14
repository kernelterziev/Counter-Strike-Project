from django.urls import path
from . import views

urlpatterns = [
    path('', views.TeamListView.as_view(), name='team_list'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),

    path('create-roster/', views.create_team_with_roster, name='create_team_roster'),
    path('<int:team_id>/roster-preview/', views.team_roster_preview, name='team_roster_preview'),
]