from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content}'
