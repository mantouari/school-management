# School Management – Déploiement Render

Projet Django minimal fonctionnel pour le déploiement sur Render.

## Lancer en local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Déployer sur Render (méthode la plus simple)

1. Poussez ce repo sur GitHub.
2. Sur Render : **New → Web Service** → connectez le repo.
3. **Environment** : `Python 3`
4. **Build Command** : `./build.sh`
5. **Start Command** : `gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -`
6. **Variables d'environnement** :
   - `SECRET_KEY`  → (générez une chaîne aléatoire longue)
   - `DEBUG` → `False`
   - `ALLOWED_HOSTS` → `.onrender.com,localhost`
   - (Optionnel) Créez un PostgreSQL dans Render : `DATABASE_URL` sera injecté automatiquement.

Ou utilisez **New → Blueprint** avec le fichier `render.yaml` à la racine.

## Pour vérifier

- `/` → page d'accueil
- `/health/` → `{"status":"ok"}`
- `/admin/` → admin Django

## Notes

- `gunicorn` écoute sur `$PORT` (fourni par Render).
- Les fichiers statiques sont servis par **WhiteNoise** (pas besoin de Nginx/CDN externe).
- Les migrations sont lancées automatiquement dans le `release` (Procfile) / dans `build.sh`.
