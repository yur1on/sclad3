# Generated by Django 5.1 on 2024-10-07 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_profile_workshop_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='workshop_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]