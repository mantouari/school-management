from django.contrib import admin
from django.db import models as dj_models
from django.forms import NumberInput

from .models import Evaluation, Note


class NoteInline(admin.TabularInline):
    model = Note
    extra = 0
    autocomplete_fields = ("eleve",)
    formfield_overrides = {
        dj_models.DecimalField: {"widget": NumberInput(attrs={"step": "0.25", "min": 0})},
    }


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("libelle", "type", "cours", "periode", "date", "note_max")
    list_filter = ("type", "periode", "cours__classe")
    search_fields = ("libelle", "cours__matiere__libelle")
    date_hierarchy = "date"
    inlines = [NoteInline]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("eleve", "evaluation", "valeur", "observation")
    list_filter = ("evaluation__periode", "evaluation__cours__classe")
    search_fields = ("eleve__nom", "eleve__prenom", "eleve__matricule")
    autocomplete_fields = ("eleve", "evaluation")
