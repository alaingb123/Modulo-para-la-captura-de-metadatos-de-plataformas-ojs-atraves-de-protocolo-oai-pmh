# Generated by Django 5.0.3 on 2024-05-25 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0012_alter_metadataformat_prefix_alter_set_set_spec'),
    ]

    operations = [
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
            ],
        ),
    ]
