# Generated by Django 5.0.7 on 2024-08-20 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_delete_blogpost_remove_telemetry_dev'),
    ]

    operations = [
        migrations.AddField(
            model_name='telemetry',
            name='burst_timer',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='telemetry',
            name='tx_frequency',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='telemetry',
            name='user_agent',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='telemetry',
            name='uploader_antenna',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
