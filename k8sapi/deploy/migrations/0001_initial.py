# Generated by Django 5.0.6 on 2024-05-25 18:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('namespace', models.CharField(max_length=100)),
                ('application_name', models.CharField(max_length=100)),
                ('deployed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(max_length=100)),
            ],
        ),
    ]
