# core/settings.py
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = \"your-secret-key-here\"

DEBUG = False

ALLOWED_HOSTS = [\"*\"]

# DATABASE - SIMPLE AND DIRECT
if \"DATABASE_URL\" in os.environ:
    # Railway - PostgreSQL
    db_url = urlparse(os.environ[\"DATABASE_URL\"])
    DATABASES = {
        \"default\": {
            \"ENGINE\": \"django.db.backends.postgresql\",
            \"NAME\": db_url.path[1:],
            \"USER\": db_url.username,
            \"PASSWORD\": db_url.password,
            \"HOST\": db_url.hostname,
            \"PORT\": db_url.port,
        }
    }
else:
    # Local - SQLite (using pysqlite3)
    DATABASES = {
        \"default\": {
            \"ENGINE\": \"django.db.backends.sqlite3\",
            \"NAME\": BASE_DIR / \"db.sqlite3\",
        }
    }

INSTALLED_APPS = [
    \"django.contrib.admin\",
    \"django.contrib.auth\",
    \"django.contrib.contenttypes\",
    \"django.contrib.sessions\",
    \"django.contrib.messages\",
    \"django.contrib.staticfiles\",
    \"django.contrib.sites\",
    \"pages\",
    \"allauth\",
    \"allauth.account\",
    \"allauth.socialaccount\",
]

MIDDLEWARE = [
    \"django.middleware.security.SecurityMiddleware\",
    \"whitenoise.middleware.WhiteNoiseMiddleware\",
    \"django.contrib.sessions.middleware.SessionMiddleware\",
    \"django.middleware.common.CommonMiddleware\",
    \"django.middleware.csrf.CsrfViewMiddleware\",
    \"django.contrib.auth.middleware.AuthenticationMiddleware\",
    \"django.contrib.messages.middleware.MessageMiddleware\",
    \"django.middleware.clickjacking.XFrameOptionsMiddleware\",
    \"allauth.account.middleware.AccountMiddleware\",
]

ROOT_URLCONF = \"core.urls\"

TEMPLATES = [
    {
        \"BACKEND\": \"django.template.backends.django.DjangoTemplates\",
        \"DIRS\": [BASE_DIR / \"templates\"],
        \"APP_DIRS\": True,
        \"OPTIONS\": {
            \"context_processors\": [
                \"django.template.context_processors.debug\",
                \"django.template.context_processors.request\",
                \"django.contrib.auth.context_processors.auth\",
                \"django.contrib.messages.context_processors.messages\",
            ],
        },
    },
]

WSGI_APPLICATION = \"core.wsgi.application\"

AUTH_PASSWORD_VALIDATORS = [
    {\"NAME\": \"django.contrib.auth.password_validation.UserAttributeSimilarityValidator\"},
    {\"NAME\": \"django.contrib.auth.password_validation.MinimumLengthValidator\"},
    {\"NAME\": \"django.contrib.auth.password_validation.CommonPasswordValidator\"},
    {\"NAME\": \"django.contrib.auth.password_validation.NumericPasswordValidator\"},
]

LANGUAGE_CODE = \"en-us\"
TIME_ZONE = \"UTC\"
USE_I18N = True
USE_TZ = True

STATIC_URL = \"/static/\"
STATICFILES_DIRS = [BASE_DIR / \"static\"]
STATIC_ROOT = BASE_DIR / \"staticfiles\"
STATICFILES_STORAGE = \"whitenoise.storage.CompressedManifestStaticFilesStorage\"

MEDIA_URL = \"/media/\"
MEDIA_ROOT = BASE_DIR / \"media\"

DEFAULT_AUTO_FIELD = \"django.db.models.BigAutoField\"

LOGIN_URL = \"/login/\"
LOGIN_REDIRECT_URL = \"/dashboard/\"
LOGOUT_REDIRECT_URL = \"/\"

SITE_ID = 1

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
