"""
Docker-optimized settings with PostgreSQL
Cloud-native configuration for containers
"""
from .settings import *
import os

# PostgreSQL Database (cloud-ready)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'agenda_db'),
        'USER': os.environ.get('POSTGRES_USER', 'agenda_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'secure_password_123'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Container networking
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']
DEBUG = os.environ.get('DEBUG', '0') == '1'

# Static files for containers  
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security for containers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Cloud Run handles SSL termination

# Logging optimized for containers
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'tareas': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
