from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .forms import GameEntryForm
from .models import GameEntry

@login_required
def add_entry(request):
    if request.method == "POST":
        form = GameEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Partie enregistrée !")
            return redirect("profile", username=request.user.username)
    else:
        form = GameEntryForm()
    return render(request, "games/add_entry.html", {"form": form})

def recent(request):
    entries = GameEntry.objects.select_related("user").order_by("-played_at")[:50]
    return render(request, "games/recent.html", {"entries": entries})

def leaderboards(request):
    # aggregate per user
    data = {}
    for e in GameEntry.objects.select_related("user").filter(verification_status="approved"):
        d = data.setdefault(e.user_id, {"user": e.user, "games": 0, "wins": 0, "kills": 0})
        d["games"] += 1
        d["kills"] += e.kills
        if e.won:
            d["wins"] += 1

    # compute ratios
    boards = []
    for u in data.values():
        deaths = u["games"] - u["wins"]
        kd = (u["kills"] / deaths) if deaths > 0 else u["kills"]
        winrate = (u["wins"] / u["games"] * 100) if u["games"] else 0
        boards.append({
            "user": u["user"],
            "games": u["games"],
            "wins": u["wins"],
            "kills": u["kills"],
            "kd": round(kd, 2),
            "winrate": round(winrate, 2),
        })

    # Sort different views
    top_kd = sorted(boards, key=lambda x: x["kd"], reverse=True)[:20]
    top_kills = sorted(boards, key=lambda x: x["kills"], reverse=True)[:20]
    top_winrate = sorted(boards, key=lambda x: (x["winrate"], x["games"]), reverse=True)[:20]

    return render(request, "games/leaderboards.html", {
        "top_kd": top_kd,
        "top_kills": top_kills,
        "top_winrate": top_winrate,
    })
