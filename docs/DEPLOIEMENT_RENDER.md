# 🚀 Guide de déploiement sur Render

Ce guide explique pas à pas comment mettre le logiciel de gestion scolaire en
production sur [Render](https://render.com). Le déploiement s'appuie
entièrement sur **Docker** : Render construit l'image depuis le `Dockerfile`
du dépôt, lance le conteneur et le connecte à une base **PostgreSQL** managée.

Deux méthodes sont proposées :

- **Méthode A — Blueprint (recommandée)** : tout est décrit dans `render.yaml`,
  Render crée l'application **et** la base en une seule opération.
- **Méthode B — Manuelle** : création des services dans le tableau de bord Render.

---

## 📋 Ce que le dépôt met déjà en place

| Élément | Rôle |
|---|---|
| `Dockerfile` | Image python:3.12-slim, utilisateur non-root, écoute sur `0.0.0.0:$PORT` |
| `docker-entrypoint.sh` | Applique les migrations, collecte les statiques, initialise les cycles/niveaux, démarre Gunicorn |
| `render.yaml` | Blueprint : service web Docker + base PostgreSQL + variables d'environnement |
| `/health/` | Sonde de santé HTTP (configurée comme health check Render) |
| `school_management/settings/prod.py` | HTTPS/HSTS, cookies sécurisés, validation stricte de `SECRET_KEY` et `ALLOWED_HOSTS` |

Render fournit automatiquement la variable `PORT` au conteneur ;
l'entrypoint démarre Gunicorn sur `0.0.0.0:${PORT:-8000}` — rien à changer.

---

## Méthode A — Déploiement via Blueprint (recommandée)

1. **Pousser le code sur GitHub** (Render se synchronise avec votre dépôt) :

   ```bash
   git remote add origin https://github.com/<votre-compte>/school-management.git
   git push -u origin main
   ```

2. **Connecter Render à GitHub** : sur [dashboard.render.com](https://dashboard.render.com),
   autorisez l'accès au dépôt (*New → Blueprint* ou lors de la sélection du dépôt).

3. **Créer le Blueprint** : *New* → **Blueprint**, sélectionnez le dépôt
   `school-management`. Render détecte `render.yaml` à la racine et vous
   propose de créer automatiquement :
   - le service web **gestion-scolaire** (runtime Docker) ;
   - la base PostgreSQL **gestion-scolaire-db**.

4. **Vérifiez le plan** puis cliquez **Apply** / **Create** :
   - `plan: starter` pour le service web (payant ~7 $/mois, disque possible) —
     ou `free` pour tester (l'application se met en veille après inactivité) ;
   - `plan: free` pour la base (suffisant pour tester ; les bases gratuites
     expirent après 30 jours — passez à `basic-256mb` minimum pour la production).

5. **Adaptez le domaine dans `render.yaml`** (avant ou après le premier déploiement) :
   Render attribue une URL du type `https://gestion-scolaire.onrender.com`.
   Mettez ce nom dans les variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_HOSTS`
   (dans `render.yaml` ou *Environment* du service), puis redéployez.

6. **Créer le premier compte administrateur** : *Dashboard → gestion-scolaire → Shell* :

   ```bash
   python manage.py createsuperuser
   ```

   > Renseignez le nom d'utilisateur, l'e-mail et un mot de passe fort.

7. (Optionnel) **Jeu de données de démonstration** :

   ```bash
   python manage.py init_demo
   ```

8. Ouvrez `https://<votre-service>.onrender.com` : 🎉 l'application est en ligne.
   L'entrypoint a déjà appliqué les migrations et initialisé les 15 niveaux
   (maternelle → lycée).

---

## Méthode B — Création manuelle des services

### 1. Créer la base PostgreSQL

*Dashboard → New → **PostgreSQL*** :

- **Name** : `gestion-scolaire-db`
- **Database** : `gestion_scolaire` · **User** : `gestion_scolaire`
- **Plan** : `free` (test) ou `basic-256mb`+ (production)

Après création, copiez la valeur **Internal Database URL**
(format `postgres://user:motdepasse@hôte/db`) — Render ajoute déjà
`?sslmode=require`.

### 2. Créer le service web Docker

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

### 3. Créer le premier compte administrateur

*Dashboard → gestion-scolaire → **Shell*** :

```bash
python manage.py createsuperuser
```

---

## 💾 Fichiers média (photos, logo…)

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

---

## 🔐 Nom de domaine personnalisé

1. *Dashboard → gestion-scolaire → Settings → Custom Domains → Add Custom Domain* ;
2. Ajoutez l'enregistrement DNS indiqué chez votre registrar (CNAME) ;
3. Mettez à jour les variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_HOSTS`
   avec votre domaine (`mon-ecole.fr,gestion-scolaire.onrender.com`) ;
4. Render émet automatiquement le certificat TLS.

---

## 🔄 Mises à jour et exploitation

| Action | Comment |
|---|---|
| **Déployer une modification** | `git push` — avec `autoDeploy: true`, Render reconstruit et redéploie. Les migrations sont appliquées automatiquement par l'entrypoint au démarrage du nouveau conteneur. |
| **Voir les logs** | *Dashboard → service → Logs* (migrations, Gunicorn, erreurs). |
| **Revenir en arrière** | *Deploys → Rollback* sur un déploiement sain. |
| **Sauvegarder la base** | *Dashboard → base PostgreSQL → Backups* (plans payants) ou `pg_dump` depuis un job. |
| **Commande ponctuelle** | *Dashboard → service → Shell* : `python manage.py <commande>` |

### Post-déploiement : checklist

- [ ] `/health/` répond `{"status": "ok"}` ;
- [ ] connexion à `/admin/` fonctionne (sinon vérifier `CSRF_TRUSTED_HOSTS`) ;
- [ ] mot de passe du superutilisateur changé ;
- [ ] fuseau horaire (`TIME_ZONE`) adapté ;
- [ ] `SECRET_KEY` générée par Render (`generateValue: true`) — ne jamais la versionner ;
- [ ] données de démonstration supprimées si nécessaire :
      `python manage.py shell` puis purge des objets de démo.

---

## 🛠️ Dépannage rapide

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

---

## 💰 Coûts indicatifs

| Configuration | Coût |
|---|---|
| Test (web `free` + PostgreSQL `free`) | 0 $ — services en veille, base expirant après 30 jours |
| Petite école (web `starter` + PostgreSQL `basic-256mb`) | ≈ 7 $/mois + ≈ 6,95 $/mois |
| + disque média 5 Go | ≈ +0,85 $/mois (0,25 $/Go/mois) |

> Les tarifs évoluent : vérifiez [render.com/pricing](https://render.com/pricing).
