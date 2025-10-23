#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Upload ALL media files (profiles, blog images, everything)
python upload_media.py

# Collect static files (will include media now)
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Import local data
python manage.py import_data
