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
              'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'desk.middleware.SessionBindingMiddleware', 'desk.middleware.SecurityPolicyMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': ['django.template.context_processors.request',
               'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
if os.environ.get('DATABASE_URL'):
    from desk.deployment import postgres_url
    DATABASES = {'default':postgres_url(os.environ['DATABASE_URL'])}
elif os.environ.get('DB_ENGINE') == 'postgresql':
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
LOGIN_REDIRECT_URL = '/'
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

# SSO remains deferred. Accept only the implemented authentication provider.
AUTH_MODE = os.environ.get('AUTH_MODE','local')
if AUTH_MODE != 'local':
    raise ImproperlyConfigured('Only local authentication is currently implemented; configure SSO after provider integration.')
AUTHENTICATION_BACKENDS = ['desk.auth_backend.PolicyBackend']
SECURITY_TRUSTED_PROXY_CIDRS = [v for v in os.environ.get('SECURITY_TRUSTED_PROXY_CIDRS','').split(',') if v]
# Enable only behind the private, non-published web service in deploy/compose.yaml.
if os.environ.get('TRUST_PROXY_HEADERS') == '1':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')

# Provider-generated host is trusted configuration, never an incoming HTTP header.
if os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
    from desk.deployment import render_host
    render_hostname=render_host(os.environ['RENDER_EXTERNAL_HOSTNAME'])
    ALLOWED_HOSTS=[h for h in ALLOWED_HOSTS if h]+[render_hostname]
    CSRF_TRUSTED_ORIGINS=CSRF_TRUSTED_ORIGINS+['https://'+render_hostname]
if os.environ.get('SERVE_STATIC') == '1':
    MIDDLEWARE.insert(1,'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},
              'staticfiles':{'BACKEND':'whitenoise.storage.CompressedStaticFilesStorage'}}

# Explicit operator-facing environment identity; DEBUG=False alone does not imply production.
STUDIO_ENVIRONMENT = os.environ.get('STUDIO_ENVIRONMENT', 'development' if DEBUG else 'unspecified')
if STUDIO_ENVIRONMENT not in ('development', 'staging', 'production', 'unspecified'):
    raise ImproperlyConfigured('STUDIO_ENVIRONMENT must be development, staging, production, or unspecified.')

PASSWORD_RESET_TIMEOUT = 3600
