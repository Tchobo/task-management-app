# Generated by Django 3.2.24 on 2024-02-19 16:16

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(null=True, upload_to=core.models.profile_image_file_path),
        ),
    ]
