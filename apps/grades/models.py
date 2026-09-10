"""
Évaluations (devoirs, compositions) et notes des élèves.
La moyenne pondérée par matière/classe est calculée dans apps.students.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.academic.models import Cours, Periode
from apps.core.models import TimeStampedModel
from apps.students.models import Eleve


class Evaluation(TimeStampedModel):
    """Évaluation : devoir surveillé, composition, interrogation..."""

    class Type(models.TextChoices):
        DEVOIR = "DEVOIR", "Devoir"
        COMPOSITION = "COMPOSITION", "Composition"
        INTERROGATION = "INTERROGATION", "Interrogation"
        PRATIQUE = "PRATIQUE", "Évaluation pratique"

    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="evaluations", verbose_name="cours")
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name="evaluations", verbose_name="période")
    libelle = models.CharField("libellé", max_length=150)  # ex. « Composition 1er trim. »
    type = models.CharField("type", max_length=15, choices=Type.choices, default=Type.DEVOIR)
    date = models.DateField("date de l'évaluation")
    note_max = models.DecimalField("note maximale", max_digits=5, decimal_places=2, default=20)

    class Meta:
        verbose_name = "évaluation"
        verbose_name_plural = "évaluations"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.libelle} — {self.cours}"

    def clean(self):
        if self.note_max is not None and self.note_max <= 0:
            raise ValidationError("La note maximale doit être strictement positive.")


class Note(TimeStampedModel):
    """Note obtenue par un élève à une évaluation."""

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name="notes", verbose_name="évaluation")
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="notes", verbose_name="élève")
    valeur = models.DecimalField(
        "note obtenue", max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Laisser vide si l'élève était absent.",
    )
    observation = models.CharField("observation", max_length=150, blank=True)

    class Meta:
        verbose_name = "note"
        verbose_name_plural = "notes"
        ordering = ["evaluation", "eleve"]
        constraints = [
            models.UniqueConstraint(fields=["evaluation", "eleve"], name="note_unique_par_eleve"),
        ]

    def __str__(self):
        if self.valeur is None:
            return f"{self.eleve.nom_complet} — absent(e) ({self.evaluation.libelle})"
        return f"{self.eleve.nom_complet} — {self.valeur}/{self.evaluation.note_max} ({self.evaluation.libelle})"

    def clean(self):
        if self.valeur is not None and self.evaluation_id and self.valeur > self.evaluation.note_max:
            raise ValidationError("La note ne peut pas dépasser la note maximale de l'évaluation.")
