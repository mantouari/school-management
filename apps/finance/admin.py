from django.contrib import admin
from django.utils.html import format_html

from .models import FraisScolarite, Paiement


@admin.register(FraisScolarite)
class FraisScolariteAdmin(admin.ModelAdmin):
    list_display = ("libelle", "annee_scolaire", "niveau", "montant", "periodicite")
    list_filter = ("annee_scolaire", "periodicite", "niveau__cycle")
    search_fields = ("libelle",)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("reference", "eleve", "frais", "montant", "mode", "date_paiement", "reste_colore")
    list_filter = ("mode", "frais__annee_scolaire")
    search_fields = ("reference", "eleve__nom", "eleve__prenom", "eleve__matricule")
    date_hierarchy = "date_paiement"
    autocomplete_fields = ("eleve", "frais")

    @admin.display(description="reste à payer")
    def reste_colore(self, obj):
        reste = obj.reste_a_payer
        if reste > 0:
            return format_html('<b style="color:#b91c1c;">{}</b>', reste)
        return format_html('<b style="color:#15803d;">soldé</b>')
