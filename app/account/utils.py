from core.models import ActiveToken
def store_active_token(user, token):
    """
    Store the active token for the user
    """
    active_token, created = ActiveToken.objects.get_or_create(user=user)
    active_token.token = token
    active_token.save()