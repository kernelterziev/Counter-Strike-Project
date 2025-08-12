from django.urls import path
from . import views

urlpatterns = [
    path('', views.TeamListView.as_view(), name='team_list'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('create/', views.TeamCreateView.as_view(), name='team_create'),
    path('<int:pk>/edit/', views.TeamUpdateView.as_view(), name='team_edit'),
    path('<int:pk>/roster/', views.team_roster, name='team_roster'),
    path('<int:pk>/join/', views.join_team, name='join_team'),
    path('<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
]