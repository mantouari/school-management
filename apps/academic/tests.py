from datetime import date

from django.core.management import call_command
from django.test import TestCase

from apps.academic.models import AnneeScolaire, Cycle, Niveau


class ReferentielsTests(TestCase):
    def test_init_referentiels_cree_les_cycles(self):
        call_command("init_referentiels", verbosity=0)
        self.assertTrue(Niveau.objects.filter(cycle=Cycle.MATERNELLE).exists())
        self.assertTrue(Niveau.objects.filter(cycle=Cycle.LYCEE).exists())
        self.assertEqual(Niveau.objects.count(), 15)  # 3 + 5 + 4 + 3

    def test_init_referentiels_est_idempotent(self):
        call_command("init_referentiels", verbosity=0)
        call_command("init_referentiels", verbosity=0)
        self.assertEqual(Niveau.objects.count(), 15)

    def test_une_seule_annee_active(self):
        a1 = AnneeScolaire.objects.create(
            libelle="2024-2025", date_debut=date(2024, 9, 1), date_fin=date(2025, 7, 1), active=True
        )
        a2 = AnneeScolaire.objects.create(
            libelle="2025-2026", date_debut=date(2025, 9, 1), date_fin=date(2026, 7, 1), active=True
        )
        a1.refresh_from_db()
        self.assertTrue(a2.active)
        self.assertFalse(a1.active)
