from django.contrib import admin
from .models import PlayerProfile

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mc_username")
    search_fields = ("user__username", "mc_username")
