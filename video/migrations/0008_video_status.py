# Generated by Django 4.2.6 on 2023-10-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0007_rename_isprocessed_video_isconverted'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='status',
            field=models.CharField(default='processing', max_length=50),
        ),
    ]