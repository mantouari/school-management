import datetime as dt

from django.test import TestCase

from apps.attendance.models import Presence
from apps.students.models import Eleve


class PresenceTests(TestCase):
    def test_presence_str(self):
        eleve = Eleve.objects.create(
            prenom="Aya", nom="KOUAME", date_naissance=dt.date(2015, 1, 1), sexe=Eleve.Sexe.F
        )
        presence = Presence.objects.create(
            eleve=eleve, date=dt.date(2026, 1, 5), statut=Presence.Statut.ABSENT, motif="Maladie"
        )
        self.assertIn("KOUAME Aya", str(presence))
        self.assertIn("Absent", str(presence))
