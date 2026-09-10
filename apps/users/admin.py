from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "telephone",
        "is_active",
    )
    list_filter = ("role", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email", "telephone")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profil gestion scolaire", {"fields": ("role", "telephone", "adresse", "photo")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profil gestion scolaire", {"fields": ("role", "telephone", "adresse", "photo")}),
    )
