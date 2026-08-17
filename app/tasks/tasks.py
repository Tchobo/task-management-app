"""Celery tasks for the tasks app.

Reminder scheduling (Phase C):
- ``check_and_send_task_reminders`` iterates every assigned task, picks the
  most-urgent unsent phase, and emails the assignee with the phase-specific
  template. ``TaskReminderLog`` is used as an idempotency guard so the same
  phase isn't sent twice for the same assignment cycle (the cycle marker is
  ``Task.assigned_at`` — see ``tasks.signals`` for how it's kept up to date).

Design decisions:
- One email per task per run (most-urgent unsent phase wins).
- Phases NOT_STARTED and MID_TERM only fire on tasks with at least 3 days
  between assignment and deadline — otherwise they'd stack on top of
  NEAR_DEADLINE and spam the assignee within a few hours.
- NEAR_DEADLINE and OVERDUE are skipped when the task sits in a category
  named exactly ``"Completed"`` — heuristic (Taskello has no explicit "done"
  field yet). See TODO in ``_is_completed_by_category_name``.
"""

from datetime import datetime, timedelta
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone

from core.models import Task, TaskReminderLog


logger = logging.getLogger(__name__)


Phase = TaskReminderLog.Phase

# Order matters: most-urgent first. On any given run, the first eligible phase
# for a task wins and nothing else is sent — dedup + priority combined.
PHASE_PRIORITY = (
    Phase.OVERDUE,
    Phase.NEAR_DEADLINE,
    Phase.MID_TERM,
    Phase.NOT_STARTED,
)

# Below this total duration (deadline - assigned_at), NOT_STARTED and MID_TERM
# are skipped to avoid stacking with NEAR_DEADLINE on short tasks.
MIN_DURATION_FOR_EARLY_PHASES = timedelta(days=3)

# The category name whose presence marks a task as done (heuristic).
COMPLETED_CATEGORY_NAME = "Completed"

# Templates + subjects per phase — kept close to the phase enum for a single
# source of truth. Subjects use light emoji + French wording matching the
# tone of the HTML templates.
_PHASE_META = {
    Phase.NOT_STARTED: (
        "reminder_not_started.html",
        "[Taskello] Rappel — une tâche vous attend",
    ),
    Phase.MID_TERM: (
        "reminder_mid_term.html",
        "[Taskello] Vous êtes à mi-chemin",
    ),
    Phase.NEAR_DEADLINE: (
        "reminder_near_deadline.html",
        "[Taskello] Deadline demain",
    ),
    Phase.OVERDUE: (
        "reminder_overdue.html",
        "[Taskello] Tâche en retard",
    ),
}


@shared_task(bind=True, ignore_result=True, name="tasks.debug_reminder_task")
def debug_reminder_task(self, message: str = "Ping from Celery"):
    """Trivial sanity-check task. Kept from Phase B for wiring diagnostics."""
    logger.warning("[tasks.debug_reminder_task id=%s] %s", self.request.id, message)
    return message


@shared_task(name="tasks.check_and_send_task_reminders", ignore_result=True)
def check_and_send_task_reminders():
    """Iterate all assigned tasks, pick the most-urgent unsent phase, send."""
    now = timezone.now()
    tasks_qs = (
        Task.objects.filter(
            assign_To__isnull=False,
            assigned_at__isnull=False,
            deadline__isnull=False,
        )
        .select_related("assign_To", "taskCategorie", "taskCategorie__dashboard")
    )

    stats = {"scanned": 0, "sent": 0, "skipped_completed": 0, "already_sent": 0, "errors": 0}

    for task in tasks_qs:
        stats["scanned"] += 1
        deadline_dt = _deadline_as_datetime(task.deadline)
        total_duration = deadline_dt - task.assigned_at

        for phase in PHASE_PRIORITY:
            if not _phase_time_matches(phase, task.assigned_at, deadline_dt, total_duration, now):
                continue

            if phase in (Phase.NEAR_DEADLINE, Phase.OVERDUE) and _is_completed_by_category_name(task):
                stats["skipped_completed"] += 1
                break  # completed = no more reminders needed at all

            if _already_sent(task, phase):
                stats["already_sent"] += 1
                continue  # try the next-priority phase

            try:
                _send_reminder_email(task, phase)
            except Exception:
                logger.exception("Failed to send reminder for task=%s phase=%s", task.id, phase)
                stats["errors"] += 1
                break

            TaskReminderLog.objects.create(
                task=task,
                user=task.assign_To,
                phase=phase.value,
                assignment_cycle_started_at=task.assigned_at,
            )
            stats["sent"] += 1
            break  # one email per task per run

    logger.info("check_and_send_task_reminders done: %s", stats)
    return stats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _deadline_as_datetime(deadline_date):
    """Convert a DateField deadline to an aware end-of-day datetime."""
    end_of_day = datetime.combine(deadline_date, datetime.max.time().replace(microsecond=0))
    return timezone.make_aware(end_of_day, timezone.get_current_timezone())


def _phase_time_matches(phase, assigned_at, deadline_dt, total_duration, now):
    """Return True if the current time crosses the trigger for this phase."""
    if phase is Phase.OVERDUE:
        return now >= deadline_dt + timedelta(hours=24)

    if phase is Phase.NEAR_DEADLINE:
        return deadline_dt - timedelta(hours=24) <= now < deadline_dt

    if phase is Phase.MID_TERM:
        if total_duration < MIN_DURATION_FOR_EARLY_PHASES:
            return False
        midpoint = assigned_at + total_duration / 2
        return now >= midpoint

    if phase is Phase.NOT_STARTED:
        if total_duration < MIN_DURATION_FOR_EARLY_PHASES:
            return False
        return now >= assigned_at + timedelta(hours=24)

    return False


def _is_completed_by_category_name(task):
    """Heuristic: task sits in a category whose name is exactly 'Completed'.

    Taskello has no explicit boolean 'done' field on Task — the closest
    signal is the column (TaskCategorie) the card sits in. Users usually
    have a column called 'Completed' or 'Done' at the end of the board.

    TODO — this only matches the literal string 'Completed'. To also accept
    'Done', 'Terminé', localized names, etc., either broaden the match or
    add a ``TaskCategorie.is_terminal`` boolean field managed from the UI.
    """
    if task.taskCategorie is None:
        return False
    return task.taskCategorie.name == COMPLETED_CATEGORY_NAME


def _already_sent(task, phase):
    """Has this phase already been sent for the current assignment cycle?"""
    return TaskReminderLog.objects.filter(
        task=task,
        phase=phase.value,
        assignment_cycle_started_at=task.assigned_at,
    ).exists()


def _send_reminder_email(task, phase):
    """Render the phase template and send the reminder email."""
    template_name, subject = _PHASE_META[phase]
    user = task.assign_To
    context = {
        "user_name": user.name or user.email.split("@")[0],
        "task_title": task.title,
        "task_deadline": task.deadline.strftime("%d/%m/%Y"),
        "dashboard_name": _dashboard_name(task),
        "dashboard_url": _dashboard_url(task),
    }
    body_html = get_template(template_name).render(context)
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    msg = EmailMessage(subject=subject, body=body_html, from_email=from_email, to=[user.email])
    msg.content_subtype = "html"
    msg.send(fail_silently=False)


def _dashboard_name(task):
    if task.taskCategorie and task.taskCategorie.dashboard:
        return task.taskCategorie.dashboard.bordName or "Taskello"
    return "Taskello"


def _dashboard_url(task):
    base = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    if task.taskCategorie and task.taskCategorie.dashboard and task.taskCategorie.dashboard.slug:
        return f"{base}/tasks/{task.taskCategorie.dashboard.slug}"
    return base
