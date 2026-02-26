from django.db import models
from apps.users.models import User
from apps.master.models import BaseClass

# Create your models here.
class Conversation(BaseClass):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_started")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations_received")

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"

    def get_other_user(self, current_user):
        return self.user2 if self.user1 == current_user else self.user1
    
class Message(BaseClass):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    isRead = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.body[:20]}"

def get_or_create_conversation(user_a, user_b):
    user1, user2 = sorted([user_a, user_b], key=lambda u: u.id)
    convo, created = Conversation.objects.get_or_create(user1=user1, user2=user2)
    return convo

