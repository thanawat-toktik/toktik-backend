# Generated by Django 4.2.6 on 2023-11-08 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0009_comment_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='like',
            old_name='isLiked',
            new_name='is_liked',
        ),
    ]
