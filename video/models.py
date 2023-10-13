from django.utils import timezone
from django.db import models

# Create your models here.

class Video(models.Model):
    id = models.AutoField(primary_key=True)
    # uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_timestamp = models.DateTimeField(default=timezone.now())
    
    s3_url_raw = models.CharField(max_length=60)
    s3_url_converted = models.CharField(max_length=60)

