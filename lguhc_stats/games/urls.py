from django.urls import path
from . import views

urlpatterns = [
    path("contributions/", views.contributions, name="contributions"),
    path("stats/", views.global_stats, name="global_stats"),
    path("modifier/<int:pk>/", views.edit_entry, name="edit_entry"),
    path("ajouter/", views.add_entry, name="add_entry"),
    path("recents/", views.recent, name="recent_entries"),
    path("classements/", views.leaderboards, name="leaderboards"),
]
