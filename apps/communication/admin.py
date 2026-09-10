from django.contrib import admin

from .models import Annonce


@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = ("titre", "cible", "importante", "date_publication", "auteur")
    list_filter = ("cible", "importante")
    search_fields = ("titre", "contenu")
    date_hierarchy = "date_publication"
