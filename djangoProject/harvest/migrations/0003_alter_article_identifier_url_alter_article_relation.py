# Generated by Django 5.0.3 on 2024-04-22 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0002_alter_anio_anio_alter_numero_numero_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='identifier_url',
            field=models.URLField(max_length=4000),
        ),
        migrations.AlterField(
            model_name='article',
            name='relation',
            field=models.URLField(max_length=4000),
        ),
    ]
