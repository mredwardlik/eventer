"""Django settings of Eventer.

Everything that differs between a laptop and a server comes from environment
variables (or a backend/.env file), with defaults that work for development:

    DJANGO_SECRET_KEY     required when DJANGO_DEBUG is off
    DJANGO_DEBUG          1 or 0, default 1
    DJANGO_ALLOWED_HOSTS  comma separated, default localhost,127.0.0.1
    CORS_ALLOWED_ORIGINS  comma separated, default http://localhost:3000
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path) -> None:
    """KEY=value lines from backend/.env, without overriding real variables."""
    if not path.is_file():
        return
    for line in path.read_text('utf-8').splitlines():
        key, sep, value = line.strip().partition('=')
        if sep and key and not key.startswith('#'):
            os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def _list(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


_load_env_file(BASE_DIR / '.env')

DEBUG = os.environ.get('DJANGO_DEBUG', '1').lower() in ('1', 'true', 'yes', 'on')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY when DJANGO_DEBUG is off.')
    SECRET_KEY = 'django-insecure-development-only-key-do-not-use-in-production'

ALLOWED_HOSTS = _list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
CORS_ALLOWED_ORIGINS = _list('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'user',
    'event',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DJANGO_DATABASE', BASE_DIR / 'db.sqlite3'),
    }
}

AUTH_USER_MODEL = 'user.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
API_PREFIX = 'api/v1/'
