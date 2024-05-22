"""
WSGI config for licenta_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "licenta_site.settings")
os.environ['GOOGLE_APPLICATION_CREDENTIALS']="./ServiceKeyGoogleCloud.json"

application = get_wsgi_application()
