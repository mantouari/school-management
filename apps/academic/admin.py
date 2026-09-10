from django.contrib import admin

from .models import AnneeScolaire, Classe, Cours, Matiere, Niveau, Periode, Seance


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ("libelle", "date_debut", "date_fin", "active")
    list_filter = ("active",)
    search_fields = ("libelle",)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ("libelle", "code", "cycle", "ordre")
    list_filter = ("cycle",)
    search_fields = ("libelle", "code")


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("libelle", "code", "active")
    list_filter = ("active",)
    search_fields = ("libelle",)


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ("libelle", "niveau", "annee_scolaire", "professeur_principal", "effectif", "capacite")
    list_filter = ("niveau__cycle", "annee_scolaire")
    search_fields = ("libelle",)
    autocomplete_fields = ("niveau", "professeur_principal")


@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin):
    list_display = ("code", "annee_scolaire", "date_debut", "date_fin", "active")
    list_filter = ("annee_scolaire", "active")


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ("matiere", "classe", "enseignant", "coefficient")
    list_filter = ("classe__niveau__cycle", "classe__annee_scolaire")
    search_fields = ("matiere__libelle", "classe__libelle")
    autocomplete_fields = ("matiere", "classe", "enseignant")


@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ("cours", "jour", "heure_debut", "heure_fin", "salle")
    list_filter = ("jour",)
    autocomplete_fields = ("cours",)
