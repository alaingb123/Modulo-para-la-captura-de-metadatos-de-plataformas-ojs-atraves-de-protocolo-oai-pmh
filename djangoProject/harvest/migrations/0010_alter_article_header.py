# Generated by Django 5.0.3 on 2024-05-07 15:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0009_remove_revista_clasificacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='header',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='harvest.header'),
        ),
    ]
