from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import GameEntry

@admin.register(GameEntry)
class GameEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "played_at", "role", "camp", "kills", "won", "verification_status", "proof_thumb")
    list_filter = ("camp", "role", "won", "played_at", "verification_status")
    search_fields = ("user__username", "killed_players", "notes")
    autocomplete_fields = ("user",)
    actions = ["approve_entries", "reject_entries"]
    readonly_fields = ("preview_proof", "verified_by", "verified_at")

    fieldsets = (
        ("Infos partie", {
            "fields": ("user", "played_at", "role", "camp", "kills", "won", "killed_players", "notes")
        }),
        ("Preuve", {
            "fields": ("proof_image", "preview_proof")
        }),
        ("Vérification", {
            "fields": ("verification_status", "verified_by", "verified_at")
        }),
    )

    # Vignette cliquable dans la liste
    def proof_thumb(self, obj):
        if obj.proof_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="height:48px;border:1px solid #333;border-radius:4px"/></a>',
                obj.proof_image.url, obj.proof_image.url
            )
        return "—"
    proof_thumb.short_description = "Preuve"

    # Aperçu grand dans la fiche
    def preview_proof(self, obj):
        if obj.proof_image:
            return format_html('<img src="{}" style="max-width:420px;max-height:420px;border:1px solid #333;border-radius:6px"/>', obj.proof_image.url)
        return "—"
    preview_proof.short_description = "Aperçu"

    # Historiser qui valide et quand
    def save_model(self, request, obj, form, change):
        if change and "verification_status" in form.changed_data:
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
        super().save_model(request, obj, form, change)

    def approve_entries(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.verification_status = "approved"
            obj.verified_by = request.user
            obj.verified_at = timezone.now()
            obj.save(update_fields=["verification_status", "verified_by", "verified_at"])
            updated += 1
        self.message_user(request, f"{updated} entrée(s) approuvée(s).")
    approve_entries.short_description = "Approuver les entrées sélectionnées"

    def reject_entries(self, request, queryset):
        updated = queryset.update(verification_status="rejected", verified_by=request.user)
        self.message_user(request, f"{updated} entrée(s) refusée(s).")
    reject_entries.short_description = "Refuser les entrées sélectionnées"
