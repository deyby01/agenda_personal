"""
Configuración para Google Cloud Run - VERSIÓN COMPLETA CON WHITENOISE
"""
from .settings import *
import os

# Configuración de producción  
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'tu-secret-key-super-seguro-cloud-2024-deyby')

# Hosts permitidos para Cloud Run
ALLOWED_HOSTS = [
    'agenda-personal-1015223170221.us-central1.run.app',
    'localhost',
    '127.0.0.1',
    '*'  # Para flexibilidad de Cloud Run
]

# CSRF orígenes de confianza
CSRF_TRUSTED_ORIGINS = [
    'https://agenda-personal-1015223170221.us-central1.run.app',
    'http://localhost:8000'
]

# Base de datos SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CRÍTICO: Configuración de archivos estáticos para Cloud Run
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# AGREGAMOS WHITENOISE PARA SERVIR CSS/JS EN PRODUCCIÓN
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MIDDLEWARE - AGREGAR WHITENOISE AL PRINCIPIO
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← AGREGAR ESTA LÍNEA
] + [m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware']

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Framework de sitios
SITE_ID = 1

# Configuraciones de seguridad para HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Cloud Run maneja terminación SSL
USE_TZ = True
TIME_ZONE = 'America/Bogota'

# Logging para Cloud Run
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}

# Configuraciones de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
