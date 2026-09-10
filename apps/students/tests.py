import datetime as dt

from django.core.management import call_command
from django.test import TestCase

from apps.academic.models import AnneeScolaire, Niveau
from apps.students.models import Eleve, Inscription


class EleveTests(TestCase):
    def setUp(self):
        call_command("init_referentiels", verbosity=0)
        self.annee = AnneeScolaire.objects.create(
            libelle="2025-2026", date_debut=dt.date(2025, 9, 1), date_fin=dt.date(2026, 7, 1)
        )
        from apps.academic.models import Classe
        self.classe = Classe.objects.create(
            libelle="CM2 A", niveau=Niveau.objects.get(code="CM2"), annee_scolaire=self.annee
        )

    def test_matricule_genere_automatiquement(self):
        eleve = Eleve.objects.create(
            prenom="Aya", nom="KOUAME",
            date_naissance=dt.date(2015, 3, 12), sexe=Eleve.Sexe.F,
        )
        self.assertEqual(len(eleve.matricule), 10)
        self.assertEqual(eleve.nom_complet, "KOUAME Aya")

    def test_age(self):
        eleve = Eleve.objects.create(
            prenom="Yao", nom="ASSI",
            date_naissance=dt.date(2012, 1, 1), sexe=Eleve.Sexe.M,
        )
        self.assertGreaterEqual(eleve.age, 14)

    def test_inscription_unique_par_annee(self):
        from django.db import IntegrityError
        eleve = Eleve.objects.create(
            prenom="Salif", nom="DIALLO",
            date_naissance=dt.date(2010, 6, 5), sexe=Eleve.Sexe.M,
        )
        Inscription.objects.create(eleve=eleve, classe=self.classe, annee_scolaire=self.annee)
        with self.assertRaises(IntegrityError):
            Inscription.objects.create(eleve=eleve, classe=self.classe, annee_scolaire=self.annee)
