"""
Settings package for budget_app.

Imports the appropriate settings module based on the DJANGO_SETTINGS_MODULE environment variable.
Default: development settings
"""

from decouple import config

# Determine which settings to use
ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'test':
    from .test import *
else:
    from .development import *
