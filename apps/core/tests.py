from django.test import TestCase


class CoreViewsTests(TestCase):
    def test_page_accueil_accessible(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_health_check(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})

    def test_tableau_de_bord_protege(self):
        response = self.client.get("/tableau-de-bord/")
        self.assertEqual(response.status_code, 302)  # redirige vers la connexion
