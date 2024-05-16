# Generated by Django 3.2.25 on 2024-04-29 14:18

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_alter_taskcategorie_indexcolor'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='slug',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]