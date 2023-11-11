from django.db import models

from authentication.models import User
from video.models import Video

NOTIFICATION_TYPE = ["like", "comment"]
NOTIFICATION_MESSAGE = {
    NOTIFICATION_TYPE[0]: "likes the video", 
    NOTIFICATION_TYPE[1]: "commented on the video"
}

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=30)  # TODO: change this to enum if possible

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_receiver")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="notifications")

    is_seen = models.BooleanField(default=False)
