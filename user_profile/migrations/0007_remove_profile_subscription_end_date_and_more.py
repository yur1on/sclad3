# Generated by Django 5.1 on 2024-11-08 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0006_profile_subscription_end_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='subscription_end_date',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='subscription_start_date',
        ),
    ]