# Generated by Django 5.0 on 2025-07-12 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gado', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
