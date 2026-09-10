"""
Crée un jeu de données de démonstration (établissement, année scolaire,
périodes, matières, classes, comptes utilisateurs et élèves).

    python manage.py init_demo                # données de démonstration
    python manage.py init_demo --superuser    # + compte admin/admin123

À utiliser pour découvrir l'outil en local — jamais en production.
"""
import datetime as dt
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.academic.models import AnneeScolaire, Classe, Cours, Matiere, Niveau, Periode, TypePeriode
from apps.core.models import Etablissement
from apps.students.models import Eleve

User = get_user_model()

MATIERES = [
    ("Lecture", "LEC"), ("Écriture", "ECR"), ("Mathématiques", "MATH"),
    ("Éveil au milieu", "EVM"), ("Français", "FRA"), ("Anglais", "ANG"),
    ("Histoire-Géographie", "HG"), ("Sciences de la Vie et de la Terre", "SVT"),
    ("Physique-Chimie", "PC"), ("Éducation Physique et Sportive", "EPS"),
    ("Philosophie", "PHILO"), ("Informatique", "INFO"),
]

PRENOMS = ["Aya", "Koffi", "Aminata", "Ibrahim", "Fatou", "Serge", "Nadège", "Yao",
           "Mariam", "Jean-Marc", "Salif", "Estelle", "Abdoulaye", "Chantal", "Bakary"]
NOMS = ["KOUAME", "TRAORE", "DIALLO", "NGUESSAN", "OUATTARA", "KONE", "BAMBA", "ASSI",
        "SANOGO", "YEO", "GBAGBO", "COULIBALY", "AKA", "DOSSO", "ZADI"]


class Command(BaseCommand):
    help = "Initialise un jeu de données de démonstration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--superuser", action="store_true",
            help="Crée aussi le compte administrateur admin / admin123.",
        )

    def handle(self, *args, **options):
        # Les référentiels (cycles/niveaux) doivent exister avant tout
        from django.core.management import call_command
        call_command("init_referentiels", verbosity=0)

        random.seed(42)  # données reproductibles


        # Établissement -------------------------------------------------------
        etab, cree = Etablissement.objects.get_or_create(
            defaults={
                "nom": "Groupe Scolaire Les Palmiers",
                "slogan": "De la maternelle au lycée, grandir ensemble",
                "ville": "Abidjan", "pays": "Côte d'Ivoire",
                "telephone": "+225 27 22 00 00 00",
                "email": "contact@lespalmiers.edu",
                "description": (
                    "Établissement privé d'enseignement général allant de la "
                    "maternelle au lycée, ouvert depuis 1998."
                ),
            }
        )
        if cree:
            self.stdout.write(f"+ Établissement « {etab.nom} »")

        # Année scolaire et périodes ------------------------------------------
        annee, cree = AnneeScolaire.objects.get_or_create(
            libelle="2025-2026",
            defaults={
                "date_debut": dt.date(2025, 9, 15),
                "date_fin": dt.date(2026, 7, 10),
                "active": True,
            },
        )
        if cree:
            self.stdout.write(f"+ Année scolaire {annee} (active)")
        for code, libelle in TypePeriode.choices[:3]:  # trimestres
            Periode.objects.get_or_create(
                annee_scolaire=annee, code=code,
                defaults={"active": code == "T1"},
            )

        # Matières -------------------------------------------------------------
        for libelle, code in MATIERES:
            Matiere.objects.get_or_create(libelle=libelle, defaults={"code": code})

        # Comptes utilisateurs ---------------------------------------------------
        if options["superuser"]:
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    "admin", "admin@lespalmiers.edu", "admin123",
                    first_name="Admin", last_name="Établissement",
                )
                self.stdout.write(self.style.WARNING(
                    "+ Compte administrateur créé : admin / admin123 "
                    "(à changer immédiatement !)"
                ))

        enseignants = []
        for i in range(6):
            username = f"prof{i+1}"
            prof, cree = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": random.choice(PRENOMS),
                    "last_name": random.choice(NOMS),
                    "role": User.Role.ENSEIGNANT,
                    "email": f"{username}@lespalmiers.edu",
                },
            )
            if cree:
                prof.set_password("prof1234")
                prof.save()
                enseignants.append(prof)
        self.stdout.write(f"+ {len(enseignants)} enseignant(s) de démonstration (prof1..prof6 / prof1234)")

        # Classes ----------------------------------------------------------------
        classes = []
        plan_classes = [
            ("PS", "PS A"), ("GS", "GS A"),
            ("CP", "CP A"), ("CM2", "CM2 A"),
            ("3EME", "3e 1"), ("TLE", "Terminale S"),
        ]
        for code_niveau, libelle in plan_classes:
            niveau = Niveau.objects.get(code=code_niveau)
            classe, cree = Classe.objects.get_or_create(
                libelle=libelle, annee_scolaire=annee,
                defaults={"niveau": niveau, "capacite": 35, "salle": f"S{random.randint(1,20)}"},
            )
            classes.append(classe)
            if cree:
                self.stdout.write(f"+ Classe {classe}")
        self.stdout.write(f"+ {len(classes)} classe(s) de démonstration")

        # Cours -------------------------------------------------------------------
        nb_cours = 0
        for classe in classes:
            matieres = random.sample(list(Matiere.objects.all()), k=4)
            for matiere in matieres:
                cours, cree = Cours.objects.get_or_create(
                    classe=classe, matiere=matiere,
                    defaults={"enseignant": random.choice(enseignants) if enseignants else None,
                              "coefficient": random.choice([1, 1, 2, 3])},
                )
                nb_cours += cree
        self.stdout.write(f"+ {nb_cours} cours de démonstration")

        # Élèves --------------------------------------------------------------------
        nb_eleves = 0
        for classe in classes:
            for _ in range(5):
                prenom, nom = random.choice(PRENOMS), random.choice(NOMS)
                eleve, cree = Eleve.objects.get_or_create(
                    prenom=prenom, nom=nom, classe=classe,
                    defaults={
                        "date_naissance": dt.date(
                            random.randint(2005, 2021), random.randint(1, 12), random.randint(1, 28)
                        ),
                        "sexe": random.choice([Eleve.Sexe.F, Eleve.Sexe.M]),
                        "lieu_naissance": "Abidjan",
                    },
                )
                nb_eleves += cree
        self.stdout.write(self.style.SUCCESS(f"+ {nb_eleves} élève(s) de démonstration"))
        self.stdout.write(self.style.SUCCESS("Démonstration prête : connectez-vous avec admin / admin123."))
