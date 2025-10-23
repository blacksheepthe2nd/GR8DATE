web: gunicorn core.wsgi:application --workers 1 --threads 2 --worker-class sync --bind 0.0.0.0:$PORT --max-requests 1000 --max-requests-jitter 100
