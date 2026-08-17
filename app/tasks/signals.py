"""Signals for the tasks app.

Currently tracks changes to ``Task.assign_To`` and updates ``Task.assigned_at``
accordingly. ``assigned_at`` is the reference timestamp used by the reminder
scheduler (``tasks.tasks.check_and_send_task_reminders``) to decide when each
reminder phase fires. Whenever the assignment cycle changes (a fresh assignee,
a reassignment, or an unassignment), the reminder log for the task becomes
conceptually stale — the scheduler uses ``assigned_at`` as the cycle marker
so a new phase sequence starts naturally.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import Task


@receiver(pre_save, sender=Task)
def update_assigned_at_on_assignee_change(sender, instance, **kwargs):
    """Keep ``Task.assigned_at`` in sync with changes to ``Task.assign_To``.

    - New task with an assignee → set ``assigned_at`` to now.
    - Existing task, assignee changed (assign / reassign) → refresh ``assigned_at``.
    - Existing task, unassigned (assign_To set to None) → clear ``assigned_at``.
    - Existing task, assignee unchanged → do nothing.
    """
    now = timezone.now()

    if instance.pk is None:
        # Creation path — no previous state to diff against.
        if instance.assign_To_id is not None:
            instance.assigned_at = now
        return

    try:
        previous = sender.objects.only("assign_To_id").get(pk=instance.pk)
    except sender.DoesNotExist:
        # Concurrent delete or bulk operation — nothing safe to do.
        return

    if previous.assign_To_id == instance.assign_To_id:
        # Assignment untouched (title/description/deadline/etc. edit).
        return

    if instance.assign_To_id is None:
        instance.assigned_at = None
    else:
        instance.assigned_at = now
