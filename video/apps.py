from django.apps import AppConfig
from django.db import connection
from django.core.management import call_command


class VideoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video'

    def ready(self):
        tables = connection.introspection.table_names()
        if "video_video" not in tables:
            call_command("migrate")
