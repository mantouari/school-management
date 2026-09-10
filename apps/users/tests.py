from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_creation_utilisateur_avec_role(self):
        user = User.objects.create_user(
            username="koffi",
            first_name="Akouvi",
            last_name="KOFFI",
            role=User.Role.ENSEIGNANT,
            password="MotDePasse#2026",
        )
        self.assertEqual(user.role, User.Role.ENSEIGNANT)
        self.assertTrue(user.est_enseignant)
        self.assertEqual(str(user), "Akouvi KOFFI")

    def test_personnel_inclut_directeur(self):
        directeur = User.objects.create_user(
            username="directrice", role=User.Role.DIRECTEUR, password="x"
        )
        self.assertTrue(directeur.est_personnel)
