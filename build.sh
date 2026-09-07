#!/usr/bin/env bash
# Script de construction pour Render
# Ce script est exécuté lors du déploiement

# Sortie en cas d'erreur
set -o errexit

# Installation des dépendances Python
pip install -r requirements.txt

# Collection des fichiers statiques
python manage.py collectstatic --no-input

# Exécution des migrations de base de données
python manage.py migrate