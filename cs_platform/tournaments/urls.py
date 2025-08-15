from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view(), name='tournament_list'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('create/', views.TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/register/', views.tournament_register, name='tournament_register'),
    path('<int:tournament_id>/admin/add-team/', views.admin_add_team, name='admin_add_team'),
    path('<int:tournament_id>/admin/remove-team/', views.admin_remove_team, name='admin_remove_team'),
    path('api/team/<int:team_pk>/', views.get_team_info, name='get_team_info'),
    path('<int:tournament_id>/delete/', views.delete_tournament, name='delete_tournament'),
    path('<int:tournament_id>/ajax-delete/', views.ajax_delete_tournament, name='ajax_delete_tournament'),
]