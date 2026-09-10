"""
Annonces et communiqués de l'établissement.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Annonce(TimeStampedModel):
    """Communiqué diffusé à tout ou partie de la communauté scolaire."""

    class Cible(models.TextChoices):
        TOUS = "TOUS", "Tout le monde"
        ENSEIGNANTS = "ENSEIGNANTS", "Enseignants"
        PARENTS = "PARENTS", "Parents"
        ELEVES = "ELEVES", "Élèves"

    titre = models.CharField("titre", max_length=200)
    contenu = models.TextField("contenu")
    cible = models.CharField("destinataires", max_length=15, choices=Cible.choices, default=Cible.TOUS)
    importante = models.BooleanField("mise en avant", default=False)
    date_publication = models.DateTimeField("date de publication", null=True, blank=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="annonces_publiees", verbose_name="auteur",
    )

    class Meta:
        verbose_name = "annonce"
        verbose_name_plural = "annonces"
        ordering = ["-date_publication", "-cree_le"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        import django.utils.timezone as tz
        if not self.date_publication:
            self.date_publication = tz.now()
        super().save(*args, **kwargs)
