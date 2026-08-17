"""Celery application bootstrap.

Discovers tasks in every Django app that ships a ``tasks.py`` module
(via ``app.autodiscover_tasks()``). Broker and result backend URLs are
read from Django settings under the ``CELERY_`` namespace.
"""

import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("taskello")

# Read config from Django settings, pulling any variable prefixed with CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py inside every installed Django app.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Trivial task used to sanity-check the Celery + Redis wiring."""
    print(f"[celery.debug_task] request={self.request!r}")
