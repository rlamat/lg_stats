from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .forms import GameEntryForm
from .models import GameEntry
from django.http import HttpResponseForbidden

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
    from django.db.models import Sum, Count, Max
    users = User.objects.all()
    boards = []
    for u in users:
        qs = GameEntry.objects.filter(user=u)
        games = qs.count()
        wins = qs.filter(won=True).count()
        kills = qs.aggregate(s=Sum("kills"))["s"] or 0
        losses = max(0, games - wins)
        kd = kills / (losses or 1)
        winrate = (wins / games * 100.0) if games else 0.0
        record = qs.aggregate(m=Max("kills"))["m"] or 0
        boards.append({
            "user": u, "games": games, "wins": wins, "kills": kills,
            "losses": losses, "kd": round(kd,2), "winrate": round(winrate,2), "record": record
        })

    def with_ranks(lst):
        out = []
        for i, item in enumerate(lst, start=1):
            d = dict(item); d["rank"] = i; out.append(d)
        return out

    rk_kd = with_ranks(sorted(boards, key=lambda x: (x["kd"], x["kills"], x["games"]), reverse=True))
    rk_kills = with_ranks(sorted(boards, key=lambda x: x["kills"], reverse=True))
    rk_winrate = with_ranks(sorted(boards, key=lambda x: (x["winrate"], x["games"]), reverse=True))
    rk_records = with_ranks(sorted(boards, key=lambda x: x["record"], reverse=True))

    top_kd, top_kills, top_winrate, top_records = rk_kd[:10], rk_kills[:10], rk_winrate[:10], rk_records[:10]

    me_rows = {}
    if request.user.is_authenticated:
        for name, full, top in [("kd", rk_kd, top_kd), ("kills", rk_kills, top_kills), ("winrate", rk_winrate, top_winrate), ("records", rk_records, top_records)]:
            mine = next((r for r in full if r["user"] == request.user), None)
            if mine and all(r["user"] != request.user for r in top):
                me_rows[name] = mine

    return render(request, "games/leaderboards.html", {
        "top_kd": top_kd,
        "top_kills": top_kills,
        "top_winrate": top_winrate,
        "top_records": top_records,
        "me_rows": me_rows,
    })


def global_stats(request):
    qs = GameEntry.objects.all()
    total_games = qs.count()

    # --- Winrate par rôle (inchangé, à ta convenance) ---
    role_stats = []
    from .models import Role, Camp
    for key, label in Role.choices:
        rq = qs.filter(role=key)
        c = rq.count()
        # Si tu veux aussi baser le winrate rôle sur le camp gagnant,
        # il faut connaître le camp du rôle : ici on garde la version simple.
        w = rq.filter(won=True).count()
        role_stats.append({
            "role": label,
            "count": c,
            "wins": w,
            "winrate": round((w/c*100.0) if c else 0.0, 2),
        })

    # --- Winrate par camp basé sur "winning_camp" ---
    # Denominateur : seulement les parties où un camp gagnant a été précisé
    total_labeled = qs.filter(winning_camp__isnull=False).count()

    camp_stats = []
    for key, label in Camp.choices:
        # occurrences = fois où les joueurs ont sélectionné ce camp comme "leur camp"
        occurrences = qs.filter(camp=key).count()

        # wins = fois où ce camp a été déclaré "camp gagnant"
        wins = qs.filter(winning_camp=key).count()

        # winrate = part des victoires de ce camp sur l'ensemble des parties étiquetées
        winrate = round((wins / total_labeled * 100.0), 2) if total_labeled else 0.0

        camp_stats.append({
            "camp": label,
            "count": occurrences,
            "wins": wins,
            "winrate": winrate,
        })

    return render(request, "games/stats.html", {
        "total_games": total_games,
        "role_stats": role_stats,
        "camp_stats": camp_stats,
    })

@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(GameEntry, pk=pk)

    # Autoriser seulement l’auteur de la game ou un staff
    if request.user != entry.user and not request.user.is_staff:
        return HttpResponseForbidden("Non autorisé.")

    if request.method == "POST":
        form = GameEntryForm(request.POST, instance=entry)
        if form.is_valid():
            obj = form.save(commit=False)

            # Repasser la vérification en "en attente" si le champ existe
            if hasattr(obj, "verification_status"):
                obj.verification_status = "pending"
            if hasattr(obj, "verified_by"):
                obj.verified_by = None
            if hasattr(obj, "verified_at"):
                obj.verified_at = None

            obj.save()
            messages.success(request, "Partie mise à jour (en attente de validation).")
            return redirect("profile", entry.user.username)
    else:
        form = GameEntryForm(instance=entry)

    return render(request, "games/edit_entry.html", {"form": form, "entry": entry})

