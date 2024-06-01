"""
WSGI config for licenta_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

current_directory = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_directory, '..', 'ServiceKeyGoogleCloud.json')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "licenta_site.settings")
os.environ['GOOGLE_APPLICATION_CREDENTIALS']=service_account_path  

application = get_wsgi_application()
