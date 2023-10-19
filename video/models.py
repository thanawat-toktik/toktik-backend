from django.utils import timezone
from django.db import models

# Create your models here.


class Video(models.Model):
    id = models.AutoField(primary_key=True)
    # uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_timestamp = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=50, default="")
    caption = models.CharField(max_length=100, blank=True)
    s3_key = models.CharField(max_length=45, blank=False, unique=True, default="")
