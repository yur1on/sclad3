# Generated by Django 5.1 on 2024-10-18 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0008_part_condition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='condition',
            field=models.CharField(choices=[('new', 'Новое'), ('used', 'Б/У')], default='new', max_length=20),
        ),
    ]
