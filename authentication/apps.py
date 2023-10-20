from django.apps import AppConfig
from django.core.management import call_command
from django.db import connection


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

    def ready(self):
        tables = connection.introspection.table_names()
        if "authentication_user" not in tables:
            call_command("migrate")
