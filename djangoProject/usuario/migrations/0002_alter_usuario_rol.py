# Generated by Django 5.0.3 on 2024-04-30 15:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='usuario.rol'),
        ),
    ]
