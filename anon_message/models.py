from django.db import models
from django.contrib.auth.models import User

class AnonMessage(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"Message to {self.receiver.username}: {self.message_content[:30]}..."