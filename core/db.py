import os
from urllib.parse import urlparse

def get_database_config():
    """Force PostgreSQL on Railway, SQLite only locally"""
    if "DATABASE_URL" in os.environ:
        # Railway environment - use PostgreSQL
        db_url = urlparse(os.environ["DATABASE_URL"])
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": db_url.path[1:],
                "USER": db_url.username,
                "PASSWORD": db_url.password,
                "HOST": db_url.hostname,
                "PORT": db_url.port,
                "CONN_MAX_AGE": 600,
            }
        }
    else:
        # Local development - use SQLite
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
