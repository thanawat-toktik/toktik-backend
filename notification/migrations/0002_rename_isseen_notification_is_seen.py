# Generated by Django 4.2.6 on 2023-11-11 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='isSeen',
            new_name='is_seen',
        ),
    ]
