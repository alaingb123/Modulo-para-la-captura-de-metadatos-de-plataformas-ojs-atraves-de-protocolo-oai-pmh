# Generated by Django 5.0.3 on 2024-04-21 17:07

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Arbitraje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Clasificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Idioma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository_name', models.CharField(max_length=255)),
                ('base_url', models.URLField()),
                ('protocol_version', models.CharField(max_length=10)),
                ('earliest_datestamp', models.DateTimeField()),
                ('deleted_record_policy', models.CharField(max_length=20)),
                ('granularity', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MetadataFormat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(max_length=50)),
                ('namespace', models.TextField()),
                ('schema', models.URLField()),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metadata_formats', to='harvest.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('datestamp', models.DateTimeField()),
                ('set_spec', models.CharField(max_length=255)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Revista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issn_e', models.CharField(max_length=8, validators=[django.core.validators.RegexValidator('^[0-9]{8}$', 'Ingrese un ISSN válido.')])),
                ('descripcion', models.TextField()),
                ('arbitraje', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='harvest.arbitraje')),
                ('autores', models.ManyToManyField(related_name='autores', to='harvest.autor')),
                ('clasificacion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='harvest.clasificacion')),
                ('editores', models.ManyToManyField(related_name='editores', to='harvest.autor')),
                ('idioma', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='harvest.idioma')),
                ('pais', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='harvest.pais')),
                ('proveedor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='harvest.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_spec', models.CharField(max_length=50)),
                ('set_name', models.CharField(max_length=255)),
                ('proveedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Volumen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volumen', models.CharField(max_length=100, unique=True)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.anio')),
            ],
        ),
        migrations.CreateModel(
            name='Numero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=100, unique=True)),
                ('volumen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.volumen')),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('creator', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('description', models.TextField()),
                ('publisher', models.TextField()),
                ('date', models.TextField()),
                ('format', models.TextField()),
                ('identifier_url', models.URLField(max_length=400)),
                ('source', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('relation', models.URLField(max_length=400)),
                ('rights', models.TextField()),
                ('resource_types', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('anio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.anio')),
                ('header', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='harvest.header')),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='harvest.idioma')),
                ('numero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.numero')),
                ('volumen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='harvest.volumen')),
            ],
        ),
    ]
