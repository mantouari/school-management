"""
Organisation pédagogique : années scolaires, cycles (maternelle → lycée),
niveaux, classes, matières, cours et emplois du temps.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import TimeStampedModel


class AnneeScolaire(TimeStampedModel):
    """Ex. « 2025-2026 ». Une seule année doit être active à la fois."""

    libelle = models.CharField("libellé", max_length=9, unique=True)  # 2025-2026
    date_debut = models.DateField("date de début")
    date_fin = models.DateField("date de fin")
    active = models.BooleanField("année en cours", default=False)

    class Meta:
        verbose_name = "année scolaire"
        verbose_name_plural = "années scolaires"
        ordering = ["-libelle"]

    def __str__(self):
        return self.libelle

    def clean(self):
        if self.date_debut and self.date_fin and self.date_fin <= self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")

    def save(self, *args, **kwargs):
        # Garantit une seule année active
        if self.active:
            AnneeScolaire.objects.exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)


class Cycle(models.TextChoices):
    """Les quatre cycles couverts par le logiciel."""

    MATERNELLE = "MATERNELLE", "Maternelle"
    ELEMENTAIRE = "ELEMENTAIRE", "Élémentaire (Primaire)"
    COLLEGE = "COLLEGE", "Collège"
    LYCEE = "LYCEE", "Lycée"


class Niveau(TimeStampedModel):
    """
    Niveau d'études rattaché à un cycle.
    Ex. Petite section (Maternelle), CM2 (Élémentaire), 3e (Collège), Terminale (Lycée).
    """

    cycle = models.CharField("cycle", max_length=20, choices=Cycle.choices)
    libelle = models.CharField("libellé", max_length=60)
    code = models.CharField("code", max_length=20)  # PS, MS, GS, CP, 6E, TLE...
    ordre = models.PositiveSmallIntegerField("ordre d'affichage", default=0)

    class Meta:
        verbose_name = "niveau"
        verbose_name_plural = "niveaux"
        ordering = ["ordre"]
        constraints = [
            models.UniqueConstraint(fields=["cycle", "code"], name="niveau_unique_par_cycle"),
        ]

    def __str__(self):
        return f"{self.libelle} ({self.get_cycle_display()})"


class Matiere(TimeStampedModel):
    """Matière enseignée (Lecture, Mathématiques, SVT, Philosophie...)."""

    libelle = models.CharField("libellé", max_length=100, unique=True)
    code = models.CharField("code", max_length=20, blank=True)
    couleur = models.CharField(
        "couleur (hexadécimal)", max_length=7, default="#2563eb", blank=True
    )
    active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "matière"
        verbose_name_plural = "matières"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle


class Classe(TimeStampedModel):
    """
    Classe réelle d'une année scolaire : « PS A », « CM2 B », « 3e 1 », « Terminale S ».
    """

    libelle = models.CharField("libellé", max_length=60)
    niveau = models.ForeignKey(Niveau, on_delete=models.PROTECT, related_name="classes", verbose_name="niveau")
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.PROTECT, related_name="classes", verbose_name="année scolaire"
    )
    professeur_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_dirigees",
        verbose_name="professeur principal",
        limit_choices_to={"role__in": ["ENSEIGNANT", "DIRECTEUR"]},
    )
    capacite = models.PositiveSmallIntegerField("capacité d'accueil", default=30)
    salle = models.CharField("salle", max_length=50, blank=True)

    class Meta:
        verbose_name = "classe"
        verbose_name_plural = "classes"
        ordering = ["niveau__ordre", "libelle"]
        constraints = [
            models.UniqueConstraint(
                fields=["libelle", "annee_scolaire"], name="classe_unique_par_annee"
            ),
        ]

    def __str__(self):
        return f"{self.libelle} — {self.annee_scolaire}"

    @property
    def effectif(self):
        return self.eleves.count()


class TypePeriode(models.TextChoices):
    """Types de périodes de notation : trimestres ou semestres."""

    TRIMESTRE_1 = "T1", "1er trimestre"
    TRIMESTRE_2 = "T2", "2e trimestre"
    TRIMESTRE_3 = "T3", "3e trimestre"
    SEMESTRE_1 = "S1", "1er semestre"
    SEMESTRE_2 = "S2", "2e semestre"


class Periode(TimeStampedModel):
    """
    Période de notation d'une année scolaire : 1er trimestre, 2e trimestre...
    """

    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.CASCADE, related_name="periodes", verbose_name="année scolaire"
    )
    code = models.CharField("code", max_length=2, choices=TypePeriode.choices)
    date_debut = models.DateField("date de début", null=True, blank=True)
    date_fin = models.DateField("date de fin", null=True, blank=True)
    active = models.BooleanField("période en cours", default=False)

    class Meta:
        verbose_name = "période"
        verbose_name_plural = "périodes"
        ordering = ["annee_scolaire", "code"]
        constraints = [
            models.UniqueConstraint(fields=["annee_scolaire", "code"], name="periode_unique_par_annee"),
        ]

    def __str__(self):
        return f"{self.get_code_display()} — {self.annee_scolaire}"

    def save(self, *args, **kwargs):
        if self.active:
            Periode.objects.filter(annee_scolaire=self.annee_scolaire).exclude(
                pk=self.pk
            ).update(active=False)
        super().save(*args, **kwargs)


class Cours(TimeStampedModel):
    """
    Enseignement d'une matière dans une classe par un enseignant donné,
    avec un coefficient propre. Sert de base aux notes et à l'emploi du temps.
    """

    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name="cours", verbose_name="classe")
    matiere = models.ForeignKey(Matiere, on_delete=models.PROTECT, related_name="cours", verbose_name="matière")
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cours_enseignes",
        verbose_name="enseignant",
        limit_choices_to={"role": "ENSEIGNANT"},
    )
    coefficient = models.PositiveSmallIntegerField("coefficient", default=1)

    class Meta:
        verbose_name = "cours"
        verbose_name_plural = "cours"
        ordering = ["classe", "matiere"]
        constraints = [
            models.UniqueConstraint(
                fields=["classe", "matiere"], name="cours_unique_par_classe"
            ),
        ]

    def __str__(self):
        return f"{self.matiere} — {self.classe}"


class Seance(TimeStampedModel):
    """
    Créneau de l'emploi du temps : un cours à un jour et une heure donnés.
    """

    class Jour(models.IntegerChoices):
        LUNDI = 1, "Lundi"
        MARDI = 2, "Mardi"
        MERCREDI = 3, "Mercredi"
        JEUDI = 4, "Jeudi"
        VENDREDI = 5, "Vendredi"
        SAMEDI = 6, "Samedi"

    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="seances", verbose_name="cours")
    jour = models.IntegerField("jour", choices=Jour.choices)
    heure_debut = models.TimeField("heure de début")
    heure_fin = models.TimeField("heure de fin")
    salle = models.CharField("salle", max_length=50, blank=True)

    class Meta:
        verbose_name = "séance (emploi du temps)"
        verbose_name_plural = "séances (emploi du temps)"
        ordering = ["jour", "heure_debut"]

    def __str__(self):
        return f"{self.get_jour_display()} {self.heure_debut:%H:%M} — {self.cours}"

    def clean(self):
        if self.heure_debut and self.heure_fin and self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être postérieure à l'heure de début.")
