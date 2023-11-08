from django.utils import timezone
from django.db import models
from authentication.models import User


class Video(models.Model):
    id = models.AutoField(primary_key=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=50, default="")
    caption = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=45, blank=False, unique=True, default="")
    view = models.IntegerField(default=0)
    isConverted = models.BooleanField(default=False)
    isChunked = models.BooleanField(default=False)
    hasThumbnail = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default="processing")

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    content = models.CharField(max_length=200, blank=True, default="")

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="likes")
    is_liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user_id", "video_id",)
