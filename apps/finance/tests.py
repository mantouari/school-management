import datetime as dt
from decimal import Decimal

from django.test import TestCase

from apps.academic.models import AnneeScolaire, Niveau
from apps.finance.models import FraisScolarite, Paiement
from apps.students.models import Eleve


class FinanceTests(TestCase):
    def setUp(self):
        self.annee = AnneeScolaire.objects.create(
            libelle="2025-2026", date_debut=dt.date(2025, 9, 1), date_fin=dt.date(2026, 7, 1)
        )
        niveau, _ = Niveau.objects.get_or_create(
            cycle="ELEMENTAIRE", code="CM2", defaults={"libelle": "CM2", "ordre": 8}
        )
        self.frais = FraisScolarite.objects.create(
            libelle="Scolarité CM2", annee_scolaire=self.annee, niveau=niveau,
            montant=Decimal("50000"), periodicite=FraisScolarite.Periodicite.ANNUEL,
        )
        self.eleve = Eleve.objects.create(
            prenom="Aya", nom="KOUAME", date_naissance=dt.date(2015, 1, 1), sexe=Eleve.Sexe.F
        )

    def test_reference_auto_et_total(self):
        p1 = Paiement.objects.create(
            eleve=self.eleve, frais=self.frais, montant=Decimal("20000"),
            date_paiement=dt.date(2025, 9, 20),
        )
        Paiement.objects.create(
            eleve=self.eleve, frais=self.frais, montant=Decimal("30000"),
            date_paiement=dt.date(2025, 10, 20),
        )
        self.assertTrue(p1.reference.startswith("PAY-"))
        self.assertEqual(Paiement.total_encaisse(self.annee), Decimal("50000"))
