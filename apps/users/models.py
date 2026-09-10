"""
Utilisateurs de la plateforme, avec un système de rôles :

  - ADMIN       : personnel administratif / informatique
  - DIRECTEUR   : direction de l'établissement
  - ENSEIGNANT  : corps enseignant (de la maternelle au lycée)
  - PARENT      : parent ou tuteur d'élèves
  - ELEVE       : élève inscrit
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        DIRECTEUR = "DIRECTEUR", "Directeur"
        ENSEIGNANT = "ENSEIGNANT", "Enseignant"
        PARENT = "PARENT", "Parent / Tuteur"
        ELEVE = "ELEVE", "Élève"

    role = models.CharField("rôle", max_length=20, choices=Role.choices, default=Role.ADMIN)
    telephone = models.CharField("téléphone", max_length=30, blank=True)
    adresse = models.CharField("adresse", max_length=255, blank=True)
    photo = models.ImageField("photo", upload_to="profils/", blank=True, null=True)

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.get_full_name() or self.username

    # Petits helpers de rôle -------------------------------------------------
    @property
    def est_enseignant(self):
        return self.role == self.Role.ENSEIGNANT

    @property
    def est_parent(self):
        return self.role == self.Role.PARENT

    @property
    def est_personnel(self):
        """Direction, administration, enseignants : accès au back-office."""
        return self.role in {self.Role.ADMIN, self.Role.DIRECTEUR, self.Role.ENSEIGNANT}

    @property
    def profession(self):
        return self.get_role_display()
