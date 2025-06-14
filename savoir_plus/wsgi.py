"""
WSGI config for Savoir+ LMS project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'savoir_plus.settings')

application = get_wsgi_application()
