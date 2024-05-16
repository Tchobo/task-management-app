# Generated by Django 3.2.25 on 2024-04-30 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_dashboard_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskcategorie',
            options={'ordering': ['indexNumber']},
        ),
        migrations.AddField(
            model_name='task',
            name='position',
            field=models.DecimalField(blank=True, decimal_places=5, default=0.0, max_digits=12, null=True),
        ),
    ]
