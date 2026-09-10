"""
Suivi des présences : absences, retards et justifications.
"""
from django.conf import settings
from django.db import models

from apps.academic.models import Cours
from apps.core.models import TimeStampedModel
from apps.students.models import Eleve


class Presence(TimeStampedModel):
    """Pointage d'un élève pour une date (et éventuellement un cours)."""

    class Statut(models.TextChoices):
        PRESENT = "PRESENT", "Présent"
        ABSENT = "ABSENT", "Absent"
        RETARD = "RETARD", "Retard"
        EXCUSE = "EXCUSE", "Absence excusée"

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="presences", verbose_name="élève")
    cours = models.ForeignKey(
        Cours, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="presences", verbose_name="cours",
    )
    date = models.DateField("date")
    statut = models.CharField("statut", max_length=10, choices=Statut.choices, default=Statut.PRESENT)
    motif = models.CharField("motif / justification", max_length=255, blank=True)
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="presences_saisies", verbose_name="saisi par",
    )

    class Meta:
        verbose_name = "présence"
        verbose_name_plural = "présences"
        ordering = ["-date", "eleve__nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["eleve", "date", "cours"], name="presence_unique_par_cours"
            ),
        ]

    def __str__(self):
        return f"{self.eleve.nom_complet} — {self.get_statut_display()} ({self.date})"
