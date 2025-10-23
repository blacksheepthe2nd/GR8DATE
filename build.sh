#!/usr/bin/env bash
set -o errexit

# Use less memory during install
pip install --no-cache-dir -r requirements.txt

# Run migrations efficiently
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --noinput --clear

echo "Build completed successfully!"
