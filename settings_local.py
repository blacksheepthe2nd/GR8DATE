# Temporary fix - add this to your settings.py after DATABASES configuration
import sys

# Use SQLite for local development if PostgreSQL isn't available
if 'test' in sys.argv or 'createsuperuser' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
