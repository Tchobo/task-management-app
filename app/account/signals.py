"""
Signal when the user try to login in the app
"""


from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(pre_save, sender=Token)
def delete_existing_tokens(sender, instance, **kwargs):
    user = instance.user
    Token.objects.filter(user=user).delete()
    