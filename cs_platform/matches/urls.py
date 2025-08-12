from django.urls import path
from . import views

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('create/', views.MatchCreateView.as_view(), name='match_create'),
    path('<int:pk>/result/', views.match_result, name='match_result'),
]