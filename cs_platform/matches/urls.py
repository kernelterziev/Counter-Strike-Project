from django.urls import path
from . import views

urlpatterns = [
    path('', views.MatchListView.as_view(), name='match_list'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('create/', views.MatchCreateView.as_view(), name='match_create'),
    path('<int:pk>/result/', views.match_result, name='match_result'),
    path('<int:match_id>/delete/', views.delete_match, name='delete_match'),
    path('<int:match_id>/ajax-delete/', views.ajax_delete_match, name='ajax_delete_match'),
path('api/stats/', views.match_stats_summary, name='match_stats_api'),

]

