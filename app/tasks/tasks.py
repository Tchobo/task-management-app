"""Celery tasks for the tasks app.

Phase B ships an infrastructure-only debug task. The real reminder logic
(4-phase reminders on task assignment) is added in Phase C.
"""

from celery import shared_task


@shared_task(bind=True, ignore_result=True, name="tasks.debug_reminder_task")
def debug_reminder_task(self, message: str = "Ping from Celery"):
    """Log a message from a Celery worker. Used to sanity-check the wiring.

    Call from a Django shell::

        from tasks.tasks import debug_reminder_task
        debug_reminder_task.delay("Hello Phase B")

    You should then see the message printed in the ``celery_worker`` container
    logs (``docker-compose logs -f celery_worker``).
    """
    print(f"[tasks.debug_reminder_task id={self.request.id}] {message}")
    return message
