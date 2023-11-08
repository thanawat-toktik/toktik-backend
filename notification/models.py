from django.db import models

from authentication.models import User
from video.models import Video

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=30) # governs how the notification will read

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="notifications")

    isSeen = models.BooleanField(default=False)
