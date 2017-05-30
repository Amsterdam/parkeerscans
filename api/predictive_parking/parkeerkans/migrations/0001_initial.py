# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 09:45
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mvp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_geometrie', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
                ('vollcode', models.CharField(blank=True, max_length=4, null=True)),
                ('naam', models.CharField(blank=True, max_length=40, null=True)),
                ('weekdag', models.FloatField(blank=True, null=True)),
                ('uur', models.FloatField(blank=True, null=True)),
                ('aantal_fiscale_vakken', models.BigIntegerField(blank=True, null=True)),
                ('verwachte_bezettingsgraad', models.DecimalField(blank=True, decimal_places=65535, max_digits=65535, null=True)),
                ('parkeerkansindicatie', models.TextField(blank=True, null=True)),
                ('betrouwbaarheid', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'mvp',
                'managed': False,
            },
        ),
    ]