# 🎓 Gestion Scolaire — de la maternelle au lycée

Logiciel complet de gestion d'établissement scolaire (maternelle, primaire, collège et lycée), écrit en **Django**, conteneurisé avec **Docker** et prêt à déployer sur **Render**.

## ✨ Fonctionnalités

| Module | Contenu |
|---|---|
| 👥 **Utilisateurs & rôles** | Administrateur, Directeur, Enseignant, Parent/Tuteur, Élève — avec comptes, photos et coordonnées |
| 🏫 **Organisation pédagogique** | Années scolaires, cycles (maternelle → lycée), 15 niveaux préchargés, classes, professeur principal, matières, cours avec coefficients, emploi du temps |
| 🎒 **Élèves** | Dossiers élèves (matricule auto, naissance, sexe, photo, infos médicales), tuteurs, inscriptions et historique annuel |
| 📝 **Vie scolaire** | Pointage des présences : absents, retards, absences excusées, motifs |
| 📊 **Notes & évaluations** | Devoirs, compositions, interrogations ; notes sur barème ; moyenne pondérée par coefficients |
| 💰 **Finances** | Barèmes de frais par niveau (mensuel/trimestriel/annuel), encaissements, reste à payer, totaux encaissés |
| 📣 **Communication** | Annonces ciblées (tous, enseignants, parents, élèves) avec mise en avant |
| 🖥️ **Interface** | Page d'accueil publique de l'établissement, tableau de bord (effectifs, encaissements, absences du jour, annonces), administration Django entièrement en français |

## 🧱 Architecture du projet

```
school-management/
├── manage.py
├── requirements.txt            # dépendances Python épinglées
├── Dockerfile                  # image de production (python:3.12-slim, non-root)
├── docker-entrypoint.sh        # migrations + collectstatic + référentiels + gunicorn
├── docker-compose.yml          # environnement de développement local (web + PostgreSQL)
├── render.yaml                 # blueprint Render (app web + base PostgreSQL)
├── .env.example                # modèle de configuration
│
├── school_management/          # configuration du projet Django
│   ├── settings/
│   │   ├── base.py             # paramètres communs (12-factor, variables d'env)
│   │   ├── dev.py              # développement (debug, console emails…)
│   │   └── prod.py             # production (HTTPS, HSTS, validation stricte)
│   ├── urls.py
│   ├── wsgi.py                 # point d'entrée gunicorn
│   └── asgi.py
│
├── apps/                       # applications métier, une par domaine
│   ├── core/                   # abstractions (TimeStampedModel), établissement, accueil & dashboard
│   ├── users/                  # modèle utilisateur personnalisé + rôles
│   ├── academic/               # cycles, niveaux, classes, matières, cours, emploi du temps
│   │   └── management/commands/init_referentiels.py   # crée cycles & niveaux
│   │   └── management/commands/init_demo.py           # jeu de données de démonstration
│   ├── students/               # élèves & inscriptions
│   ├── attendance/             # présences
│   ├── grades/                 # évaluations & notes
│   ├── finance/                # frais de scolarité & paiements
│   └── communication/          # annonces
│
├── templates/                  # templates globaux (accueil, tableau de bord, connexion)
├── static/                     # CSS / JS / images
└── docs/
    └── GUIDE_DEPLOIEMENT.md      # ⭐ guide complet : local (1) puis Render (2)
```

**Choix techniques :**
- **Django 5.2 LTS** (support long terme), Python 3.12 ;
- **PostgreSQL** en production (Render) et en local via Docker — SQLite par défaut hors Docker pour faciliter les premiers pas ;
- **Gunicorn** (serveur WSGI) + **WhiteNoise** (fichiers statiques compressés) ;
- **python-decouple + dj-database-url** : toute la configuration passe par des variables d'environnement (12-factor) ;
- Conteneur **non-root**, configurations de sécurité HTTPS/HSTS activées en production.

## 🚀 Démarrage rapide (local, avec Docker)

Prérequis : [Docker](https://docs.docker.com/get-docker/) et Docker Compose.

```bash
# 1. Construire et lancer (web + base PostgreSQL)
docker compose up --build

# 2. Dans un second terminal, créer les données de démonstration
docker compose exec web python manage.py init_demo --superuser
```

Puis ouvrir :

| URL | Description |
|---|---|
| http://localhost:8000/ | Page d'accueil de l'établissement |
| http://localhost:8000/admin/ | Administration (`admin` / `admin123` — **à changer**) |
| http://localhost:8000/tableau-de-bord/ | Tableau de bord (après connexion) |
| http://localhost:8000/health/ | Sonde de santé (utilisée par Render) |

## 🧪 Démarrage sans Docker (optionnel)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py init_demo --superuser
python manage.py runserver
```

Sans `DATABASE_URL`, le projet utilise automatiquement SQLite.

## 🧰 Commandes utiles

```bash
python manage.py init_referentiels   # crée/met à jour cycles & niveaux (idempotent)
python manage.py init_demo           # données de démonstration
python manage.py test                # lance la suite de tests
python manage.py check --deploy      # audit de configuration de production
```

## 🌍 Déploiement sur Render

Le dépôt contient tout le nécessaire :

- un **Dockerfile** compatible Render (écoute sur `0.0.0.0:$PORT`, health check `/health/`) ;
- un **blueprint `render.yaml`** qui provisionne l'application **et** la base PostgreSQL en une seule opération ;
- les **settings de production** sécurisés.

👉 Suivez le guide complet : **[docs/GUIDE_DEPLOIEMENT.md](docs/GUIDE_DEPLOIEMENT.md)**

## ✅ Tests

```bash
docker compose exec web python manage.py test    # sous Docker
# ou localement : python manage.py test
```

La suite couvre : rôles utilisateurs, référentiels cycles/niveaux, unicité des inscriptions,
validation des notes, totaux de paiements, pages publiques et protection du tableau de bord.

## 📄 Licence

Projet fourni à titre pédagogique — adaptez-le librement aux besoins de votre établissement.
