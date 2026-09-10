import datetime as dt
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic.models import AnneeScolaire, Classe, Cours, Matiere, Niveau, Periode
from apps.grades.models import Evaluation, Note
from apps.students.models import Eleve


class NotesTests(TestCase):
    def setUp(self):
        call = Niveau.objects.get_or_create(
            cycle="ELEMENTAIRE", code="CM2", defaults={"libelle": "CM2", "ordre": 8}
        )[0]
        annee = AnneeScolaire.objects.create(
            libelle="2025-2026", date_debut=dt.date(2025, 9, 1), date_fin=dt.date(2026, 7, 1)
        )
        periode = Periode.objects.create(annee_scolaire=annee, code="T1", active=True)
        classe = Classe.objects.create(libelle="CM2 A", niveau=call, annee_scolaire=annee)
        matiere = Matiere.objects.create(libelle="Mathématiques", code="MATH")
        cours = Cours.objects.create(classe=classe, matiere=matiere, coefficient=2)
        eleve = Eleve.objects.create(
            prenom="Aya", nom="KOUAME", date_naissance=dt.date(2015, 1, 1), sexe=Eleve.Sexe.F, classe=classe
        )
        eval_ = Evaluation.objects.create(
            cours=cours, periode=periode, libelle="Devoir n°1", date=dt.date(2025, 10, 2)
        )
        self.note = Note.objects.create(evaluation=eval_, eleve=eleve, valeur=Decimal("15.5"))

    def test_note_str(self):
        self.assertIn("15.5", str(self.note))

    def test_note_ne_depasse_pas_note_max(self):
        self.note.valeur = Decimal("25")
        with self.assertRaises(ValidationError):
            self.note.clean()
