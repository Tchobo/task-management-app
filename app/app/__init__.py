"""Django project package.

Loads the Celery application on import so that the shared ``@shared_task``
decorator can register tasks even before Celery itself starts (Django
autodiscovery relies on this).
"""

from .celery import app as celery_app


__all__ = ("celery_app",)
