# Generated by Django 5.1 on 2024-08-31 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0012_remove_part_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]