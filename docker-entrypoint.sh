#!/bin/sh
# ==========================================================================
# Point d'entrée du conteneur : prépare la base et les fichiers statiques
# puis démarre gunicorn. Fonctionne en local (docker compose) comme sur
# Render (la variable PORT est fournie par la plateforme).
# ==========================================================================
set -e

echo ">> Application des migrations..."
python manage.py migrate --noinput

echo ">> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo ">> Initialisation des référentiels (cycles et niveaux)..."
python manage.py init_referentiels

echo ">> Démarrage de gunicorn..."
exec gunicorn school_management.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --access-logfile - \
    --error-logfile -
