from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Import signal handlers so they get registered at app startup.
        # noqa: F401 — the import is the side effect.
        from tasks import signals  # noqa: F401
