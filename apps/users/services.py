from .models import ConnectionRequest
from django.db import models

def getExistingRequest(sender,receiver):
    existing_request = ConnectionRequest.objects.filter(
        (models.Q(sender=sender, receiver=receiver) | 
         models.Q(sender=receiver, receiver=sender))
            ).distinct().first()
    return existing_request

def send_connection_request(sender, receiver):
    if sender == receiver:
        return None

    connection, created = ConnectionRequest.objects.get_or_create(
        sender=sender,
        receiver=receiver
    )
    return connection

def getConnections(user):
    result  = ConnectionRequest.objects.filter(
        models.Q(sender = user, status="accepted")|
        models.Q(receiver = user,status="accepted")
    ).distinct()

    return result

def getConnectionsCount(user):
    return getConnections(user).count()

def getPendingConnections(user):
    result  = ConnectionRequest.objects.filter(
        models.Q(sender = user, status="pending")|
        models.Q(receiver = user,status="pending")
    ).distinct()

    return result

def getPendingConnectionsCount(user):
    return getPendingConnections(user).count()


def accept_connection(sender, receiver):
    try:
        connection = ConnectionRequest.objects.get(
            sender=sender,
            receiver=receiver
        )
        connection.is_accepted = True
        connection.save()
        return True
    except ConnectionRequest.DoesNotExist:
        return False


