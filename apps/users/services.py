from .models import ConnectionRequest
from django.db import models

def getExistingRequest(sender,receiver):
    existing_request = ConnectionRequest.objects.filter(
        (models.Q(sender=sender, receiver=receiver) | 
         models.Q(sender=receiver, receiver=sender))
            ).first()
    return existing_request