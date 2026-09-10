"""
Modèles transverses : abstractions communes et établissement scolaire.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstrait : ajoute les dates de création et de modification."""

    cree_le = models.DateTimeField("créé le", auto_now_add=True)
    modifie_le = models.DateTimeField("modifié le", auto_now=True)

    class Meta:
        abstract = True


class Etablissement(models.Model):
    """
    Informations de l'établissement (de la maternelle au lycée).
    Une seule fiche est normalement nécessaire : elle alimente la page
    d'accueil et les documents.
    """

    nom = models.CharField("nom de l'établissement", max_length=200)
    slogan = models.CharField("slogan / devise", max_length=200, blank=True)
    logo = models.ImageField("logo", upload_to="etablissement/", blank=True, null=True)
    adresse = models.CharField("adresse", max_length=255, blank=True)
    ville = models.CharField("ville", max_length=100, blank=True)
    pays = models.CharField("pays", max_length=100, blank=True)
    telephone = models.CharField("téléphone", max_length=30, blank=True)
    email = models.EmailField("adresse e-mail", blank=True)
    site_web = models.URLField("site web", blank=True)
    description = models.TextField("présentation", blank=True)

    class Meta:
        verbose_name = "établissement"
        verbose_name_plural = "établissements"

    def __str__(self):
        return self.nom

    @classmethod
    def get_solo(cls):
        """Retourne la fiche unique de l'établissement (la crée si absente)."""
        obj = cls.objects.first()
        return obj if obj is not None else cls.objects.create(nom="Mon établissement")
