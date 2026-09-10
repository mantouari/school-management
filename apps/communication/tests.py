from django.test import TestCase

from apps.communication.models import Annonce


class AnnonceTests(TestCase):
    def test_annonce_str_et_publication_auto(self):
        annonce = Annonce.objects.create(titre="Réunion des parents", contenu="Samedi à 9h.")
        self.assertIsNotNone(annonce.date_publication)
        self.assertIn("Réunion des parents", str(annonce))
