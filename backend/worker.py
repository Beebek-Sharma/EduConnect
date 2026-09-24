import os

from django.core.wsgi import get_wsgi_application
from workers import wsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = get_wsgi_application()

# Standard Django WSGI entry point for Cloudflare Python Workers.
Default = wsgi.entrypoint(application)
