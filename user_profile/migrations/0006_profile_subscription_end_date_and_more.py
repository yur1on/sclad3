# Generated by Django 5.1 on 2024-10-27 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_bookmark'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='subscription_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
