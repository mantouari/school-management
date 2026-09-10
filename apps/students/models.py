"""
Élèves et inscriptions.
"""
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Avg

from apps.academic.models import AnneeScolaire, Classe, Periode
from apps.core.models import TimeStampedModel


class Eleve(TimeStampedModel):
    """
    Élève inscrit dans l'établissement, de la maternelle au lycée.
    Le compte utilisateur associé est optionnel (utile surtout à partir
    du collège).
    """

    class Sexe(models.TextChoices):
        M = "M", "Masculin"
        F = "F", "Féminin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fiche_eleve",
        verbose_name="compte utilisateur",
    )
    matricule = models.CharField("matricule", max_length=20, unique=True, blank=True)
    prenom = models.CharField("prénom", max_length=60)
    nom = models.CharField("nom", max_length=60)
    date_naissance = models.DateField("date de naissance")
    lieu_naissance = models.CharField("lieu de naissance", max_length=100, blank=True)
    sexe = models.CharField("sexe", max_length=1, choices=Sexe.choices)
    photo = models.ImageField("photo", upload_to="eleves/", blank=True, null=True)

    # Classe suivie cette année (dénormalisation pratique)
    classe = models.ForeignKey(
        Classe, on_delete=models.PROTECT, related_name="eleves", verbose_name="classe", null=True, blank=True,
    )

    # Tuteur / parent responsable
    tuteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enfants",
        verbose_name="parent / tuteur",
        limit_choices_to={"role": "PARENT"},
    )
    contact_urgence = models.CharField("contact d'urgence", max_length=100, blank=True)
    infos_medicales = models.TextField("informations médicales", blank=True)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "élève"
        verbose_name_plural = "élèves"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule or 'sans matricule'})"

    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"

    @property
    def age(self):
        import datetime
        today = datetime.date.today()
        return today.year - self.date_naissance.year - (
            (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
        )

    def moyenne_generale(self, periode=None):
        """
        Moyenne pondérée par les coefficients des cours pour une période
        (ou toute l'année si periode est None). Retourne None sans notes.
        """
        from apps.grades.models import Note

        notes = Note.objects.filter(eleve=self, valeur__isnull=False)
        if periode is not None:
            notes = notes.filter(evaluation__periode=periode)

        moyennes_par_cours = (
            notes.values("evaluation__cours", "evaluation__cours__coefficient")
            .annotate(moyenne=Avg("valeur"))
        )
        total_pondere = Decimal("0")
        total_coeffs = Decimal("0")
        for ligne in moyennes_par_cours:
            coeff = Decimal(ligne["evaluation__cours__coefficient"] or 1)
            total_pondere += Decimal(str(ligne["moyenne"])) * coeff
            total_coeffs += coeff
        if total_coeffs == 0:
            return None
        return round(total_pondere / total_coeffs, 2)


class Inscription(TimeStampedModel):
    """
    Inscription (ou réinscription) d'un élève dans une classe pour une
    année scolaire. Historise le parcours de l'élève.
    """

    class Statut(models.TextChoices):
        EN_COURS = "EN_COURS", "En cours"
        VALIDE = "VALIDE", "Année validée"
        TRANSFERE = "TRANSFERE", "Transféré"
        ABANDON = "ABANDON", "Abandon"

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="inscriptions", verbose_name="élève")
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name="inscriptions", verbose_name="classe")
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.PROTECT, related_name="inscriptions", verbose_name="année scolaire"
    )
    date_inscription = models.DateField("date d'inscription", null=True, blank=True)
    statut = models.CharField("statut", max_length=15, choices=Statut.choices, default=Statut.EN_COURS)
    observation = models.TextField("observation", blank=True)

    class Meta:
        verbose_name = "inscription"
        verbose_name_plural = "inscriptions"
        ordering = ["-annee_scolaire__libelle", "eleve__nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["eleve", "annee_scolaire"], name="inscription_unique_par_annee"
            ),
        ]

    def __str__(self):
        return f"{self.eleve.nom_complet} → {self.classe.libelle} ({self.annee_scolaire})"
