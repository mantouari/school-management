# 🚀 Guide de déploiement — Gestion scolaire

Ce guide couvre **toutes les étapes**, dans l'ordre :

1. **Partie 1 — Installation et mise en route en local** (sur votre machine, avec Docker ou sans Docker) ;
2. **Partie 2 — Déploiement en production sur Render** (à n'envisager qu'une fois l'application validée en local).

> 💡 Le passage du local vers Render ne demande **aucune modification du code** :
> seule la configuration change (variables d'environnement). Voir l'annexe en fin de guide.

---

# Partie 1 — Installation et mise en route en local

## 1.1 Prérequis

| Option | Nécessite |
|---|---|
| **A. Avec Docker** *(recommandé)* | [Docker](https://docs.docker.com/get-docker/) + Docker Compose (inclus dans Docker Desktop) — c'est tout ! |
| **B. Sans Docker** | Python 3.11+ ; PostgreSQL en option (sinon SQLite automatique) |

Récupérez le projet :

```bash
git clone https://github.com/<votre-compte>/school-management.git
cd school-management
```

*(ou décompressez l'archive `gestion-scolaire.zip` que vous avez reçue et entrez dans le dossier).*

## 1.2 Méthode A — Lancer l'application avec Docker (recommandé)

Tout est prêt : le `docker-compose.yml` lance l'application **et** une base
PostgreSQL 16, applique les migrations et initialise les référentiels
(cycles et niveaux) au démarrage.

```bash
# 1. Construire les images et démarrer (web + base de données)
docker compose up --build
```

Attendez quelques secondes, puis **dans un second terminal**, chargez les
données de démonstration et créez le compte administrateur :

```bash
# 2. Jeu de données de démonstration + compte admin/admin123
docker compose exec web python manage.py init_demo --superuser
```

Ouvrez ensuite dans votre navigateur :

| URL | Description |
|---|---|
| http://localhost:8000/ | Page d'accueil publique de l'établissement |
| http://localhost:8000/admin/ | Administration (connexion : `admin` / `admin123` — **à changer immédiatement**) |
| http://localhost:8000/tableau-de-bord/ | Tableau de bord (effectifs, encaissements, absences, annonces) |
| http://localhost:8000/health/ | Sonde de santé (utilisée par Render en production) |

Comptes de démonstration créés par `init_demo` :

| Compte | Mot de passe | Rôle |
|---|---|---|
| `admin` | `admin123` | Administrateur |
| `prof1` … `prof6` | `prof1234` | Enseignants |

> 🛑 **Changez ces mots de passe** avant toute utilisation réelle.

Pour arrêter : `Ctrl+C` dans le premier terminal, puis `docker compose down`.
Les données PostgreSQL sont conservées dans le volume `postgres_data`.

## 1.3 Méthode B — Sans Docker (environnement virtuel Python)

Utile si Docker n'est pas disponible. Sans `DATABASE_URL`, le projet
utilise automatiquement **SQLite** (parfait pour tester).

```bash
# 1. Environnement virtuel + dépendances
python3 -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configuration minimale (optionnelle en dev)
cp .env.example .env

# 3. Base de données + référentiels + démonstration
python manage.py migrate
python manage.py init_demo --superuser

# 4. Démarrer le serveur de développement
python manage.py runserver
```

Les mêmes URL que ci-dessus sont disponibles sur http://127.0.0.1:8000/.

### Variante : PostgreSQL local

Si vous préférez tester avec PostgreSQL en local (plus proche de la production) :

```bash
export DATABASE_URL=postgres://school:school@localhost:5432/school
python manage.py migrate && python manage.py init_demo --superuser
```

## 1.4 Vérifier que tout fonctionne

```bash
# Suite de tests automatisée (16 tests : modèles, vues, sécurité)
python manage.py test              # sans Docker
docker compose exec web python manage.py test   # avec Docker

# Vérification de la configuration
python manage.py check
```

## 1.5 Premiers pas dans l'application

1. Connectez-vous sur `/admin/` avec `admin / admin123` ;
2. **Changez le mot de passe** (en haut à droite → *Change password*) ;
3. Renseignez la fiche de **votre établissement** (*Noyau → Établissements*) : nom, logo, coordonnées ;
4. Créez l'**année scolaire** (*Organisation pédagogique → Années scolaires*) et cochez « année en cours » ;
   les **cycles et niveaux** (PS → Terminale) sont déjà préchargés ;
5. Créez vos **classes**, **matières** et **cours** ;
6. Inscrivez les **élèves** et affectez-les à leurs classes ;
7. Gérez au quotidien : **présences**, **évaluations/notes**, **frais et paiements**, **annonces**.

## 1.6 Commandes utiles en local

```bash
python manage.py init_referentiels    # crée/met à jour cycles & niveaux (idempotent)
python manage.py init_demo            # données de démonstration
python manage.py createsuperuser      # compte administrateur « propre »
python manage.py makemigrations       # après modification des modèles
python manage.py migrate              # applique les migrations
python manage.py test                 # lance les tests
```

---

# Partie 2 — Déploiement en production sur Render

Une fois l'application validée en local, déployez-la sur
[Render](https://render.com). Le déploiement s'appuie entièrement sur
**Docker** : Render construit l'image depuis le `Dockerfile` du dépôt, lance
le conteneur et le connecte à une base **PostgreSQL** managée.

Deux méthodes :

- **Méthode A — Blueprint (recommandée)** : tout est décrit dans `render.yaml`,
  Render crée l'application **et** la base en une seule opération.
- **Méthode B — Manuelle** : création des services dans le tableau de bord Render.

## 2.1 Ce que le dépôt met déjà en place

| Élément | Rôle |
|---|---|
| `Dockerfile` | Image python:3.12-slim, utilisateur non-root, écoute sur `0.0.0.0:$PORT` |
| `docker-entrypoint.sh` | Applique les migrations, collecte les statiques, initialise les cycles/niveaux, démarre Gunicorn |
| `render.yaml` | Blueprint : service web Docker + base PostgreSQL + variables d'environnement |
| `/health/` | Sonde de santé HTTP (configurée comme health check Render) |
| `school_management/settings/prod.py` | HTTPS/HSTS, cookies sécurisés, validation stricte de `SECRET_KEY` et `ALLOWED_HOSTS` |

Render fournit automatiquement la variable `PORT` au conteneur ;
l'entrypoint démarre Gunicorn sur `0.0.0.0:${PORT:-8000}` — rien à changer.

## 2.2 Checklist avant de déployer

- [ ] L'application fonctionne en local (Partie 1) et les tests passent ;
- [ ] Le code est poussé sur **GitHub** (Render se synchronise avec votre dépôt) :

  ```bash
  git remote add origin https://github.com/<votre-compte>/school-management.git
  git push -u origin main
  ```

- [ ] Les données de **démonstration ne seront pas déployées** (elles ne vivent
  que dans votre base locale — en production, vous partez d'une base vide).

## 2.3 Méthode A — Déploiement via Blueprint (recommandée)

1. **Connecter Render à GitHub** : sur [dashboard.render.com](https://dashboard.render.com),
   autorisez l'accès au dépôt lors de la création du service.

2. **Créer le Blueprint** : *New* → **Blueprint**, sélectionnez le dépôt
   `school-management`. Render détecte `render.yaml` à la racine et vous
   propose de créer automatiquement :
   - le service web **gestion-scolaire** (runtime Docker) ;
   - la base PostgreSQL **gestion-scolaire-db**.

3. **Vérifiez le plan** puis cliquez **Apply** / **Create** :
   - `plan: starter` pour le service web (payant ~7 $/mois, disque possible) —
     ou `free` pour tester (l'application se met en veille après inactivité) ;
   - `plan: free` pour la base (suffisant pour tester ; les bases gratuites
     expirent après 30 jours — passez à `basic-256mb` minimum pour la production).

4. **Adaptez le domaine dans `render.yaml`** (avant ou après le premier déploiement) :
   Render attribue une URL du type `https://gestion-scolaire.onrender.com`.
   Mettez ce nom dans les variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_HOSTS`
   (dans `render.yaml` ou *Environment* du service), puis redéployez.

5. **Créer le premier compte administrateur** : *Dashboard → gestion-scolaire → Shell* :

   ```bash
   python manage.py createsuperuser
   ```

   > Renseignez le nom d'utilisateur, l'e-mail et un mot de passe fort.

6. **Renseignez la fiche de votre établissement** dans l'admin
   (comme en local, section 1.5) — cette fois dans la base de production.

7. Ouvrez `https://<votre-service>.onrender.com` : 🎉 l'application est en ligne.
   L'entrypoint a déjà appliqué les migrations et initialisé les 15 niveaux
   (maternelle → lycée).

## 2.4 Méthode B — Création manuelle des services

### Étape 1 — Créer la base PostgreSQL

*Dashboard → New → **PostgreSQL*** :

- **Name** : `gestion-scolaire-db`
- **Database** : `gestion_scolaire` · **User** : `gestion_scolaire`
- **Plan** : `free` (test) ou `basic-256mb`+ (production)

Après création, copiez la valeur **Internal Database URL**
(format `postgres://user:motdepasse@hôte/db`) — Render ajoute déjà
`?sslmode=require`.

### Étape 2 — Créer le service web Docker

*Dashboard → New → **Web Service*** → connectez votre dépôt :

- **Runtime** : `Docker` (Render détecte le `Dockerfile` à la racine)
- **Instance Type** : `Free` pour tester, `Starter` pour la production
- **Health Check Path** : `/health/`

Ajoutez ensuite les **variables d'environnement** (*Environment*) :

| Clé | Valeur | Note |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `school_management.settings.prod` | |
| `SECRET_KEY` | une longue chaîne aléatoire | générez avec `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DATABASE_URL` | l'URL interne de la base | lien secret **Internal Database URL** |
| `ALLOWED_HOSTS` | `gestion-scolaire.onrender.com` | votre domaine Render (ou personnalisé) |
| `CSRF_TRUSTED_HOSTS` | `gestion-scolaire.onrender.com` | indispensable pour les formulaires (connexion, admin) |
| `WEB_CONCURRENCY` | `3` | nombre de workers Gunicorn |
| `TIME_ZONE` | `Africa/Abidjan` | adaptez à votre fuseau |

Cliquez **Create Web Service** : Render construit l'image, lance le
conteneur ; l'entrypoint applique les migrations, collecte les fichiers
statiques et initialise les référentiels, puis Gunicorn écoute sur `$PORT`.

### Étape 3 — Créer le premier compte administrateur

*Dashboard → gestion-scolaire → **Shell*** :

```bash
python manage.py createsuperuser
```

## 2.5 💾 Fichiers média (photos, logo…)

Les fichiers uploadés (photos des élèves, logo de l'établissement) sont écrits
dans `/app/media` **à l'intérieur du conteneur** : ils sont perdus à chaque
redéploiement. Deux solutions :

### Option 1 — Disque Render (simple)

1. Passez le service sur un plan payant (les **disques ne sont pas disponibles
   sur le plan gratuit**) ;
2. *Dashboard → gestion-scolaire → Disks → Add Disk* :
   - **Mount path** : `/app/media`
   - **Size** : 1 à 5 Go selon les besoins
3. Ajoutez la variable `MEDIA_ROOT=/app/media` puis redéployez.

> ⚠️ Sur Render, un disque est rattaché à **une seule instance** et n'est pas
> répliqué : adapté à une petite école mono-serveur.

### Option 2 — Stockage objet S3/R2 (recommandé en production)

Pour plusieurs instances ou une meilleure durabilité, branchez
`django-storages` avec un bucket S3 (AWS, Cloudflare R2, Scaleway…) et
définissez `MEDIA_ROOT`/`STORAGES` en conséquence.

## 2.6 🔐 Nom de domaine personnalisé

1. *Dashboard → gestion-scolaire → Settings → Custom Domains → Add Custom Domain* ;
2. Ajoutez l'enregistrement DNS indiqué chez votre registrar (CNAME) ;
3. Mettez à jour les variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_HOSTS`
   avec votre domaine (`mon-ecole.fr,gestion-scolaire.onrender.com`) ;
4. Render émet automatiquement le certificat TLS.

## 2.7 🔄 Mises à jour et exploitation

| Action | Comment |
|---|---|
| **Déployer une modification** | `git push` — avec `autoDeploy: true`, Render reconstruit et redéploie. Les migrations sont appliquées automatiquement par l'entrypoint au démarrage du nouveau conteneur. |
| **Voir les logs** | *Dashboard → service → Logs* (migrations, Gunicorn, erreurs). |
| **Revenir en arrière** | *Deploys → Rollback* sur un déploiement sain. |
| **Sauvegarder la base** | *Dashboard → base PostgreSQL → Backups* (plans payants) ou `pg_dump` depuis un job. |
| **Commande ponctuelle** | *Dashboard → service → Shell* : `python manage.py <commande>`. |

### Checklist post-déploiement

- [ ] `/health/` répond `{"status": "ok"}` ;
- [ ] connexion à `/admin/` fonctionne (sinon vérifier `CSRF_TRUSTED_HOSTS`) ;
- [ ] mot de passe du superutilisateur changé ;
- [ ] fuseau horaire (`TIME_ZONE`) adapté ;
- [ ] `SECRET_KEY` générée par Render (`generateValue: true`) — ne jamais la versionner ;
- [ ] sauvegardes de la base activées.

## 2.8 🛠️ Dépannage rapide

| Symptôme | Cause probable / solution |
|---|---|
| Build échoue | Vérifiez `requirements.txt` et le `Dockerfile` dans les logs de build. |
| **« SECRET_KEY par défaut détectée en production »** | La variable `SECRET_KEY` n'est pas définie sur le service — ajoutez-la puis redéployez. |
| **« ALLOWED_HOSTS doit contenir le domaine de production »** | Renseignez `ALLOWED_HOSTS` avec votre domaine Render. |
| Erreur **403 CSRF** à la connexion | Ajoutez le domaine dans `CSRF_TRUSTED_HOSTS`. |
| Déploiement resté bloqué puis annulé | Le health check `/health/` ne répond pas : consultez les logs (souvent une erreur de `DATABASE_URL` ou une migration en échec). |
| Page en veille / lente au premier clic (plan gratuit) | Le service gratuit s'endort après 15 min d'inactivité ; le premier réveil prend ~30 s. |
| Fichiers média perdus après redéploiement | Montez un disque Render sur `/app/media` ou utilisez un stockage S3. |
| « connection to server failed » | La base et le service web doivent être dans **la même région** ; utilisez l'URL **interne** de la base. |

## 2.9 💰 Coûts indicatifs

| Configuration | Coût |
|---|---|
| Test (web `free` + PostgreSQL `free`) | 0 $ — services en veille, base expirant après 30 jours |
| Petite école (web `starter` + PostgreSQL `basic-256mb`) | ≈ 7 $/mois + ≈ 6,95 $/mois |
| + disque média 5 Go | ≈ +0,85 $/mois (0,25 $/Go/mois) |

> Les tarifs évoluent : vérifiez [render.com/pricing](https://render.com/pricing).

---

# Annexe — Ce qui change entre le local et la production

| Aspect | Local (Partie 1) | Production Render (Partie 2) |
|---|---|---|
| Settings Django | `school_management.settings.dev` (défaut) | `school_management.settings.prod` |
| Base de données | SQLite ou PostgreSQL du Compose | PostgreSQL managée Render (`DATABASE_URL`) |
| `DEBUG` | `1` | `0` (forcé) |
| Serveur HTTP | `runserver` (dev) | Gunicorn via `docker-entrypoint.sh` |
| Fichiers statiques | servis par Django/WhiteNoise finders | collectés puis servis par WhiteNoise (compressés) |
| HTTPS | non (http://localhost) | oui, TLS géré par Render + HSTS |
| Variables d'env | `.env` facultatif | obligatoires : `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_HOSTS` |
| Données | `init_demo` autorisé | **jamais** — créez de vraies données via l'admin |

Le code et les conteneurs sont **identiques** : c'est la configuration
(variables d'environnement) qui fait la différence — c'est l'approche
« 12-factor app ».
