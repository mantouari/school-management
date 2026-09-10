"""
Frais de scolarité et paiements encaissés.
"""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from apps.academic.models import AnneeScolaire, Niveau
from apps.core.models import TimeStampedModel
from apps.students.models import Eleve


class FraisScolarite(TimeStampedModel):
    """
    Barème de frais applicable à un niveau pour une année scolaire
    (scolarité mensuelle, inscription, cantine, transport...).
    """

    class Periodicite(models.TextChoices):
        MENSUEL = "MENSUEL", "Mensuel"
        TRIMESTRIEL = "TRIMESTRIEL", "Trimestriel"
        ANNUEL = "ANNUEL", "Annuel"
        UNIQUE = "UNIQUE", "Frais unique"

    libelle = models.CharField("libellé", max_length=150)  # ex. « Scolarité CM2 »
    annee_scolaire = models.ForeignKey(
        AnneeScolaire, on_delete=models.CASCADE, related_name="frais", verbose_name="année scolaire"
    )
    niveau = models.ForeignKey(
        Niveau, on_delete=models.PROTECT, related_name="frais", verbose_name="niveau"
    )
    montant = models.DecimalField(
        "montant", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    periodicite = models.CharField(
        "périodicité", max_length=12, choices=Periodicite.choices, default=Periodicite.MENSUEL
    )

    class Meta:
        verbose_name = "frais de scolarité"
        verbose_name_plural = "frais de scolarité"
        ordering = ["annee_scolaire", "niveau__ordre", "libelle"]

    def __str__(self):
        return f"{self.libelle} — {self.montant} ({self.get_periodicite_display()})"


class Paiement(TimeStampedModel):
    """Paiement effectué par (ou pour) un élève."""

    class Mode(models.TextChoices):
        ESPECES = "ESPECES", "Espèces"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        VIREMENT = "VIREMENT", "Virement bancaire"
        CHEQUE = "CHEQUE", "Chèque"
        CARTE = "CARTE", "Carte bancaire"

    reference = models.CharField("référence", max_length=30, unique=True, blank=True)
    eleve = models.ForeignKey(Eleve, on_delete=models.PROTECT, related_name="paiements", verbose_name="élève")
    frais = models.ForeignKey(FraisScolarite, on_delete=models.PROTECT, related_name="paiements", verbose_name="frais concernés")
    montant = models.DecimalField(
        "montant payé", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date_paiement = models.DateField("date du paiement")
    mode = models.CharField("mode de paiement", max_length=15, choices=Mode.choices, default=Mode.ESPECES)
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="paiements_saisis", verbose_name="enregistré par",
    )
    observation = models.CharField("observation", max_length=255, blank=True)

    class Meta:
        verbose_name = "paiement"
        verbose_name_plural = "paiements"
        ordering = ["-date_paiement", "-id"]

    def __str__(self):
        return f"{self.reference} — {self.eleve.nom_complet} ({self.montant})"

    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            self.reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @classmethod
    def total_encaisse(cls, annee_scolaire=None):
        qs = cls.objects.all()
        if annee_scolaire is not None:
            qs = qs.filter(frais__annee_scolaire=annee_scolaire)
        return qs.aggregate(total=Sum("montant"))["total"] or 0

    @property
    def reste_a_payer(self):
        """Reste dû par l'élève sur les mêmes frais que ce paiement."""
        paye = Paiement.objects.filter(eleve=self.eleve_id, frais=self.frais_id).aggregate(
            total=Sum("montant")
        )["total"] or 0
        return self.frais.montant - paye
