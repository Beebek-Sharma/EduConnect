import os

from django_cf import DjangoCF
from workers import WorkerEntrypoint

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")


class Default(DjangoCF, WorkerEntrypoint):
    """Cloudflare Worker entry point for the EduConnect Django API."""

    def get_app(self):
        from backend.wsgi import application

        return application
