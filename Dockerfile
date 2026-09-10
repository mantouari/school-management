# ==========================================================================
# Image Docker du logiciel de gestion scolaire
# Utilisée en local (docker compose) et en production (Render, runtime Docker)
# ==========================================================================
FROM python:3.12-slim

# Empêche Python d'écrire les .pyc et active les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=school_management.settings.prod

WORKDIR /app

# Dépendances Python (couche mise en cache tant que requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Utilisateur applicatif non-root (bonne pratique sécurité)
RUN groupadd --system django && useradd --system --gid django --home /app django

# Code de l'application
COPY --chown=django:django . .

# Répertoires writables (fichiers média uploadés, statiques collectés)
RUN mkdir -p /app/media /app/staticfiles && chown -R django:django /app

USER django

EXPOSE 8000

# L'entrypoint : migrations + collectstatic + référentiels, puis gunicorn
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
