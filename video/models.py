from django.utils import timezone
from django.db import models
from authentication.models import User


class Video(models.Model):
    id = models.AutoField(primary_key=True)
    uploader = models.ForeignKey( User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=50, default="")
    caption = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=36, blank=False, unique=True, default="")
    view = models.IntegerField(default=0)
    isProcessed = models.BooleanField(default=False)
