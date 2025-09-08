from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignUpForm
from games.models import GameEntry
from django.db.models import Sum, Count, Max
from games.models import GameEntry, Role, Camp
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode

def home(request):
    # Simple dashboard / landing with some aggregate stats
    total_entries = GameEntry.objects.count()
    total_kills = GameEntry.objects.aggregate(k=Sum("kills"))["k"] or 0
    total_players = User.objects.count()
    recent_entries = GameEntry.objects.select_related("user").order_by("-played_at")[:9]
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
    profile_user = get_object_or_404(User, username=username)
    # Les parties du joueur, plus récentes en premier
    entries = GameEntry.objects.filter(user=profile_user).order_by('-played_at')

    # Cartes récap
    games = entries.count()
    wins = entries.filter(won=True).count()
    kills = entries.aggregate(s=Sum('kills'))['s'] or 0
    losses = max(0, games - wins)
    kd = round(kills / (losses or 1), 2)
    winrate = round((wins / games * 100.0), 2) if games else 0.0

    # Comptages simples (comme tu les utilisais déjà)
    role_counts = entries.values('role').annotate(c=Count('id')).order_by('-c')
    camp_counts = entries.values('camp').annotate(c=Count('id')).order_by('-c')

    # ➜ Record de kills
    record_kills = entries.aggregate(m=Max('kills'))['m'] or 0

    # ➜ Détail des rôles : nb, % apparition, % winrate
    role_wins = entries.filter(won=True).values('role').annotate(w=Count('id'))
    win_map = {r['role']: r['w'] for r in role_wins}

    role_details = []
    for rc in role_counts:
        role_key = rc['role']
        c = rc['c']
        w = win_map.get(role_key, 0)
        freq = round((c / games * 100.0), 2) if games else 0.0
        wr = round((w / c * 100.0), 2) if c else 0.0
        # Affiche le libellé humain si défini dans TextChoices
        role_label = dict(Role.choices).get(role_key, role_key)
        role_details.append({
            'role': role_label,
            'count': c,
            'freq': freq,
            'winrate': wr,
        })
        
    # Stats infection
    infected_count = entries.filter(infected=True).count()
    infected_rate = round((infected_count / games * 100.0), 2) if games else 0.0

    return render(request, "core/profile.html", {
        "profile_user": profile_user,
        "entries": entries,

        # cartes récap
        "games": games, "wins": wins, "kills": kills, "kd": kd, "winrate": winrate,

        # anciens blocs
        "role_counts": role_counts,
        "camp_counts": camp_counts,

        # ➜ nouveaux pour ton template
        "record_kills": record_kills,
        "role_details": role_details,
        
        "infected_count": infected_count,
        "infected_rate": infected_rate,
    })


def players_list(request):
    q = (request.GET.get("q") or "").strip()

    qs = User.objects.all().order_by("username")
    if q:
        qs = qs.filter(username__icontains=q)

    paginator = Paginator(qs, 24)  # 18 joueurs par page
    page_number = request.GET.get("page") or 1
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Prépare un préfixe d’URL pour la pagination qui préserve la recherche
    qs_str = urlencode({"q": q}) if q else ""
    prefix = f"?{qs_str}&page=" if qs_str else "?page="

    return render(request, "core/players.html", {
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "q": q,
        "prefix": prefix,  # <-- on l’utilise dans le template
    })
