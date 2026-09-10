from django.contrib import admin

from .models import Eleve, Inscription


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0
    autocomplete_fields = ("classe",)


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = (
        "matricule", "nom", "prenom", "sexe", "age",
        "classe", "tuteur", "actif",
    )
    list_filter = ("actif", "sexe", "classe__niveau__cycle")
    search_fields = ("matricule", "nom", "prenom")
    autocomplete_fields = ("classe", "tuteur")
    inlines = [InscriptionInline]
    fieldsets = (
        ("Identité", {"fields": ("matricule", "prenom", "nom", "sexe", "date_naissance", "lieu_naissance", "photo")}),
        ("Scolarité", {"fields": ("classe", "user", "actif")}),
        ("Contacts", {"fields": ("tuteur", "contact_urgence")}),
        ("Santé", {"fields": ("infos_medicales",), "classes": ("collapse",)}),
    )


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ("eleve", "classe", "annee_scolaire", "date_inscription", "statut")
    list_filter = ("statut", "annee_scolaire")
    search_fields = ("eleve__nom", "eleve__prenom", "eleve__matricule")
    autocomplete_fields = ("eleve", "classe")
