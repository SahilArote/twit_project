from django.db import models
from django.contrib.auth.models import User
from twit.models import twit


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(twit, on_delete=models.CASCADE, null=True, blank=True)  # shared post

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"
