from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Ensure only one chat session per user pair

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # Text may be empty if file is attached
    timestamp = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(blank=True, null=True)  # URL to the uploaded file
    file_type = models.CharField(max_length=100, blank=True, null=True)  # MIME type

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
