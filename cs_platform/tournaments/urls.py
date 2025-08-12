from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view(), name='tournament_list'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('create/', views.TournamentCreateView.as_view(), name='tournament_create'),
    path('<int:pk>/register/', views.tournament_register, name='tournament_register'),
]