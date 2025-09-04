from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignUpForm
from games.models import GameEntry
from django.db.models import Sum, Count

def home(request):
    # Simple dashboard / landing with some aggregate stats
    total_entries = GameEntry.objects.count()
    total_kills = GameEntry.objects.aggregate(k=Sum("kills"))["k"] or 0
    total_players = User.objects.count()
    recent_entries = GameEntry.objects.select_related("user").order_by("-played_at")[:10]
    return render(request, "core/home.html", {
        "total_entries": total_entries,
        "total_kills": total_kills,
        "total_players": total_players,
        "recent_entries": recent_entries,
    })

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte créé ! Vous pouvez vous connecter.")
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    entries = GameEntry.objects.filter(user=user).order_by("-played_at")
    games = entries.count()
    wins = entries.filter(won=True).count()
    deaths = games - wins  # hypothèse: mort = partie non gagnée
    kills = entries.aggregate(s=Sum("kills"))["s"] or 0

    kd = kills / deaths if deaths > 0 else kills  # eviter division par zéro
    winrate = (wins / games)*100 if games > 0 else 0

    # Rôle et camp (team) distributions
    role_counts = entries.values("role").annotate(c=Count("id")).order_by("-c")
    camp_counts = entries.values("camp").annotate(c=Count("id")).order_by("-c")

    return render(request, "core/profile.html", {
        "profile_user": user,
        "entries": entries[:20],
        "games": games,
        "wins": wins,
        "deaths": deaths,
        "kills": kills,
        "kd": round(kd, 2),
        "winrate": round(winrate, 2),
        "role_counts": role_counts,
        "camp_counts": camp_counts,
    })
