FROM python:3.11-slim

# Variables d'environnement pour éviter les .pyc et bufferiser stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Installer les dépendances système nécessaires à psycopg2/Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Collecte des statiques (SECRET_KEY factice pour build)
RUN python manage.py collectstatic --no-input \
        --settings=school_management.settings || true

EXPOSE 8000

# Render injecte $PORT ; on l'utilise
CMD ["sh", "-c", "gunicorn school_management.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile - --error-logfile -"]
