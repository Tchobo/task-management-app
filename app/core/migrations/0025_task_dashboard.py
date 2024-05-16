# Generated by Django 3.2.25 on 2024-04-10 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_taskcomment_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='dashboard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dashboards', to='core.dashboard'),
        ),
    ]