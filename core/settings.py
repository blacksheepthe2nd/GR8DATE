# DATABASE CONFIGURATION - FORCE POSTGRESQL ON RAILWAY
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

# If we're on Railway (DATABASE_URL exists), use PostgreSQL ONLY
if DATABASE_URL:
    # Force PostgreSQL configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE'),
            'USER': os.environ.get('PGUSER'),
            'PASSWORD': os.environ.get('PGPASSWORD'),
            'HOST': os.environ.get('PGHOST'),
            'PORT': os.environ.get('PGPORT', 5432),
        }
    }
    
    # Update with dj_database_url for additional settings
    db_from_env = dj_database_url.config(conn_max_age=600)
    DATABASES['default'].update(db_from_env)
else:
    # Use SQLite only for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
