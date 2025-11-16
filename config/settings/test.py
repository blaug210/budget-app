"""
Test settings for budget_app project.
"""

from .base import *

# Test mode
DEBUG = True

# In-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='budget_app_test'),
        'USER': config('DB_USER', default='budget_user'),
        'PASSWORD': config('DB_PASSWORD', default='budget_pass'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'TEST': {
            'NAME': 'budget_app_test',
        }
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable migrations for faster tests (optional)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#
#     def __getitem__(self, item):
#         return None
#
# MIGRATION_MODULES = DisableMigrations()

# Logging for tests (minimal)
LOGGING['root']['level'] = 'ERROR'
