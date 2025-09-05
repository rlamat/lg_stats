from django import forms
from .models import GameEntry
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


class GameEntryForm(forms.ModelForm):
    class Meta:
        model = GameEntry
        fields = [
            "played_at", "role", "camp", "kills", "won",
            "killed_players", "notes", "proof_image",
            "infected", "rating", "winning_camp"
        ]
        widgets = {
            "played_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "rating": forms.NumberInput(attrs={"min": 0, "max": 10, "step": 1}),
        }
        labels = {
            "played_at": "Date & heure",
            "role": "Rôle",
            "camp": "Camp",
            "kills": "Nombre de kills",
            "won": "Victoire ?",
            "killed_players": "Joueurs tués (pseudos)",
            "notes": "Commentaire",
            "winning_camp": "Camp gagnant",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cap à maintenant + 10 min
        now_local_plus = timezone.localtime(timezone.now()) + timedelta(minutes=10)
        self.fields["played_at"].widget.attrs.update({
            "max": now_local_plus.strftime("%Y-%m-%dT%H:%M"),
            "step": "60",
        })

        # Le champ "Camp gagnant" reste facultatif (sera forcé si won=True)
        if "winning_camp" in self.fields:
            self.fields["winning_camp"].required = False

        # Lire l'état actuel (POST si form bindé, sinon instance)
        data = self.data if self.is_bound else None
        if data:
            won_raw = data.get("won")
            won_val = str(won_raw).lower() in ("1", "true", "on", "yes")
            camp_val = data.get("camp") or getattr(self.instance, "camp", None)
        else:
            won_val = bool(getattr(self.instance, "won", False))
            camp_val = getattr(self.instance, "camp", None)

        # Si on a coché "Victoire ?", on verrouille winning_camp et on le cale visuellement sur camp
        if won_val and "winning_camp" in self.fields:
            self.fields["winning_camp"].disabled = True
            # valeur affichée dans le select
            self.fields["winning_camp"].initial = camp_val
            self.fields["winning_camp"].help_text = "Déduit automatiquement de votre camp (partie gagnée)."

    def clean(self):
        cleaned = super().clean()
        won = cleaned.get("won")
        camp = cleaned.get("camp")

        # Si victoire, imposer winning_camp = camp (sécurité côté serveur)
        if won and "winning_camp" in self.fields:
            cleaned["winning_camp"] = camp
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)

        # Toujours en attente tant que non modérée
        if hasattr(obj, "verification_status"):
            obj.verification_status = "pending"

        # Double sécurité : si victoire, forcer winning_camp au camp
        if getattr(obj, "won", False) and hasattr(obj, "winning_camp"):
            obj.winning_camp = obj.camp

        if commit:
            obj.save()
        return obj

    def clean_played_at(self):
        dt = self.cleaned_data.get("played_at")
        if not dt:
            return dt
        # s'assurer que le datetime est aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        allowed_max = timezone.now() + timedelta(minutes=10)
        if dt > allowed_max:
            raise ValidationError("La date/heure ne peut pas être dans le futur (marge de 10 minutes maximum).")
        return dt
