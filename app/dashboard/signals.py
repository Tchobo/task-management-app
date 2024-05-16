"""
Signal when the a dashboard is been created 
"""

from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
)

from core.models import Dashboard, TaskCategorie


@receiver(post_save, sender=Dashboard)
def create_taskCategorie(sender, instance, created, **kwargs):
    if sender.__name__ == "Dashboard":
        if created:
            category_baxklog = TaskCategorie.objects.create( name="Backlog", indexColor="rgb(33, 33, 33, 1)", indexNumber=60000.00, defaultTaskCategory=True, dashboard=instance)
            category_preogress = TaskCategorie.objects.create( name="In Progress", indexColor="rgba(106, 81, 255, 1)", indexNumber=120000.00, defaultTaskCategory=True, dashboard=instance)
            category_complete = TaskCategorie.objects.create( name="Completed", indexColor="rgba(51, 170, 68, 1)", indexNumber=180000.00, defaultTaskCategory=True, dashboard=instance)
            category_review = TaskCategorie.objects.create( name="Review", indexColor="rgba(231, 73, 46, 1)", indexNumber=240000.00, defaultTaskCategory=True, dashboard=instance)
    else:
        print("It is an update")

    
    