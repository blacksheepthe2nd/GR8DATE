# core/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()  # Load environment variables

BASE_DIR = Path(__file__).resolve().parent.parent

# Use environment variable for secret key with fallback
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Debug mode based on environment
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# CSRF and Allowed Hosts for Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

ALLOWED_HOSTS = [
    'gr8date.onrender.com', 
    '.onrender.com', 
    'gr8date.com.au',
    '.gr8date.com.au',
    'www.gr8date.com.au',
    'localhost', 
    '127.0.0.1'
]

import os
import dj_database_url

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        # Force PostgreSQL on Render
        conn_health_checks=True,
    )
}

# If on Render, ensure we use PostgreSQL
if 'RENDER' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',  # COMMENTED OUT - allauth dependency
    
    'pages',
    # 'allauth',  # COMMENTED OUT - temporarily disabled
    # 'allauth.account',  # COMMENTED OUT - temporarily disabled
    # 'allauth.socialaccount',  # COMMENTED OUT - temporarily disabled
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',  # COMMENTED OUT - allauth dependency
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SITE_ID = 1  # COMMENTED OUT - allauth dependency

# Allauth configuration - TEMPORARILY DISABLED
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',  # COMMENTED OUT
]

# Allauth settings - COMMENTED OUT (temporarily disabled)
# ACCOUNT_LOGIN_METHODS = {'username'}
# ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']
# ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_LOGOUT_ON_GET = True

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Add this for production security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
