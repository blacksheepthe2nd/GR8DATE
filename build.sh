#!/usr/bin/env bash
set -o errexit

echo "Starting build process..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --run-syncdb
python manage.py migrate sites
python manage.py migrate allauth
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
