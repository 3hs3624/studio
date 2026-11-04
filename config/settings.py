import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DEBUG', '0') == '1'
SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY is required; use DEBUG=1 for local development only.')
    SECRET_KEY = 'local-development-only-do-not-deploy-this-key'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1],testserver' if DEBUG else '').split(',')
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
                  'django.contrib.messages', 'django.contrib.staticfiles', 'desk']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'desk.middleware.RequestIDMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
              'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': ['django.template.context_processors.request',
               'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
if os.environ.get('DB_ENGINE') == 'postgresql':
    DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': os.environ['DB_NAME'],
                  'USER': os.environ['DB_USER'], 'PASSWORD': os.environ.get('DB_PASSWORD', ''),
                  'HOST': os.environ.get('DB_HOST', 'localhost'), 'PORT': os.environ.get('DB_PORT', '5432')}}
else:
    if not DEBUG:
        raise ImproperlyConfigured('Production requires DB_ENGINE=postgresql.')
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.environ.get('SQLITE_PATH',BASE_DIR / 'db.sqlite3'),
                             'OPTIONS': {'timeout': 15}}}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/portal/incidents'
LOGOUT_REDIRECT_URL = '/login/'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
CSRF_TRUSTED_ORIGINS = [s for s in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if s]
CSRF_FAILURE_VIEW = 'desk.api.csrf_failure'
DATA_UPLOAD_MAX_MEMORY_SIZE = 65536
SESSION_COOKIE_AGE = 28800
SESSION_SAVE_EVERY_REQUEST = False
