# Generated by Django 4.2.6 on 2023-10-26 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0005_merge_20231019_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='hasThumbnail',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='video',
            name='isChunked',
            field=models.BooleanField(default=False),
        ),
    ]