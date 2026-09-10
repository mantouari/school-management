from django.contrib import admin

from .models import Presence


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("eleve", "date", "statut", "cours", "motif", "enregistre_par")
    list_filter = ("statut", "date", "cours__classe")
    search_fields = ("eleve__nom", "eleve__prenom", "eleve__matricule")
    date_hierarchy = "date"
    autocomplete_fields = ("eleve", "cours")
