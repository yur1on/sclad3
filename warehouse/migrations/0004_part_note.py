# Generated by Django 5.1 on 2024-10-15 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_alter_part_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
