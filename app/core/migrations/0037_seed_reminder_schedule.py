"""Data migration — seed the periodic Beat schedule for task reminders.

Creates (idempotently) an IntervalSchedule of 1 hour and a PeriodicTask that
runs ``tasks.check_and_send_task_reminders`` on that interval. Editable from
Django admin afterwards (Periodic tasks section) if you want to change the
frequency without a code deploy.
"""

from django.db import migrations


TASK_NAME = "Check and send task reminders (hourly)"
TASK_PATH = "tasks.check_and_send_task_reminders"
INTERVAL_EVERY = 1
INTERVAL_PERIOD = "hours"  # matches django_celery_beat's IntervalSchedule.PERIOD_CHOICES


def seed_reminder_schedule(apps, schema_editor):
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=INTERVAL_EVERY,
        period=INTERVAL_PERIOD,
    )
    PeriodicTask.objects.update_or_create(
        name=TASK_NAME,
        defaults={
            "interval": schedule,
            "task": TASK_PATH,
            "enabled": True,
            "description": (
                "Iterates every assigned task and sends the appropriate reminder "
                "(NOT_STARTED / MID_TERM / NEAR_DEADLINE / OVERDUE) if the phase "
                "threshold has been crossed and the reminder hasn't been sent yet "
                "for the current assignment cycle."
            ),
        },
    )


def remove_reminder_schedule(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name=TASK_NAME).delete()
    # IntervalSchedule is intentionally left in place — other tasks may share it.


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0036_auto_20260816_2213"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(seed_reminder_schedule, reverse_code=remove_reminder_schedule),
    ]
