web: gunicorn school_management.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -
release: python manage.py migrate --no-input
