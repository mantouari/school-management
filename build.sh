#!/usr/bin/env bash
# Script de construction pour Render (Build Command)
# Sortie en cas d'erreur
set -o errexit

echo "==> Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "==> Application des migrations..."
python manage.py migrate --no-input

echo "==> Build terminé."
