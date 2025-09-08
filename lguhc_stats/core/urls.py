from django.urls import path
from . import views

urlpatterns = [
    path("joueurs/", views.players_list, name="players"),
    path("inscription/", views.signup, name="signup"),
    path("profil/<str:username>/", views.profile, name="profile"),
]
