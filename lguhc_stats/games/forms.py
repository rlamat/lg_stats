from django import forms
from .models import GameEntry
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


class GameEntryForm(forms.ModelForm):
    class Meta:
        model = GameEntry
        fields = ["played_at", "role", "camp", "kills", "won", "killed_players", "notes", "proof_image"]
        widgets = {
            "played_at": forms.DateTimeInput(attrs={"type":"datetime-local"}),
            "notes": forms.Textarea(attrs={"rows":3}),
        }
        labels = {
            "played_at": "Date & heure",
            "role": "Rôle",
            "camp": "Camp",
            "kills": "Nombre de kills",
            "won": "Victoire ?",
            "killed_players": "Joueurs tués (pseudos)",
            "notes": "Notes",
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # max = maintenant + 10 minutes (au format HTML datetime-local)
        now_local_plus = timezone.localtime(timezone.now()) + timedelta(minutes=10)
        self.fields["played_at"].widget.attrs.update({
            "max": now_local_plus.strftime("%Y-%m-%dT%H:%M"),
            "step": "60",  # optionnel: pas d'une minute
        })

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.verification_status = "pending"   # toujours en attente
        if commit:
            obj.save()
        return obj
    
    def clean_played_at(self):
        dt = self.cleaned_data.get("played_at")
        if not dt:
            return dt
        # S'assurer que le datetime est aware
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        allowed_max = timezone.now() + timedelta(minutes=10)
        if dt > allowed_max:
            raise ValidationError("La date/heure ne peut pas être dans le futur (marge de 10 minutes maximum).")
        return dt

