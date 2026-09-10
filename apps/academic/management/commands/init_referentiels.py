"""
Crée (de façon idempotente) les cycles et niveaux du système scolaire,
de la maternelle au lycée. Exécutée automatiquement au démarrage du
conteneur et après chaque déploiement.
"""
from django.core.management.base import BaseCommand

from apps.academic.models import Cycle, Niveau

REFERENTIEL = {
    Cycle.MATERNELLE: [
        ("PS", "Petite section", 1),
        ("MS", "Moyenne section", 2),
        ("GS", "Grande section", 3),
    ],
    Cycle.ELEMENTAIRE: [
        ("CP", "CP", 4),
        ("CE1", "CE1", 5),
        ("CE2", "CE2", 6),
        ("CM1", "CM1", 7),
        ("CM2", "CM2", 8),
    ],
    Cycle.COLLEGE: [
        ("6EME", "6e", 9),
        ("5EME", "5e", 10),
        ("4EME", "4e", 11),
        ("3EME", "3e", 12),
    ],
    Cycle.LYCEE: [
        ("2NDE", "2nde", 13),
        ("1ERE", "1re", 14),
        ("TLE", "Terminale", 15),
    ],
}


class Command(BaseCommand):
    help = "Initialise les cycles et niveaux (maternelle → lycée)."

    def handle(self, *args, **options):
        total = 0
        for cycle, niveaux in REFERENTIEL.items():
            for code, libelle, ordre in niveaux:
                _, cree = Niveau.objects.get_or_create(
                    cycle=cycle,
                    code=code,
                    defaults={"libelle": libelle, "ordre": ordre},
                )
                total += cree
        self.stdout.write(
            self.style.SUCCESS(
                f"Référentiels à jour — {total} niveau(x) créé(s), "
                f"{Niveau.objects.count()} au total."
            )
        )
