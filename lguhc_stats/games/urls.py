from django.urls import path
from . import views

urlpatterns = [
    path("ajouter/", views.add_entry, name="add_entry"),
    path("recents/", views.recent, name="recent_entries"),
    path("classements/", views.leaderboards, name="leaderboards"),
]
