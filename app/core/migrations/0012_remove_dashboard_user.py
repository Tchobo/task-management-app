# Generated by Django 3.2.24 on 2024-03-04 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_dashboard_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dashboard',
            name='user',
        ),
    ]
