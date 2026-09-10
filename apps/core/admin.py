from django.contrib import admin

from .models import Etablissement


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "telephone", "email")
    search_fields = ("nom", "ville")
    fieldsets = (
        ("Identité", {"fields": ("nom", "slogan", "logo", "description")}),
        ("Coordonnées", {"fields": ("adresse", "ville", "pays", "telephone", "email", "site_web")}),
    )
