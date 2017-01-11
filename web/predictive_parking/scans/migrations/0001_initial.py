# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 12:11
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parkeervak',
            fields=[
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('straatnaam', models.CharField(db_index=True, max_length=300)),
                ('soort', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=20)),
                ('aantal', models.IntegerField()),
                ('geometrie', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('bgt_wegdeel', models.CharField(db_index=True, max_length=38, null=True)),
                ('bgt_wegdeel_functie', models.CharField(db_index=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scan_id', models.IntegerField()),
                ('scan_moment', models.DateTimeField()),
                ('scan_source', models.CharField(db_index=True, max_length=15)),
                ('afstand', models.CharField(max_length=25, null=True)),
                ('latitude', models.DecimalField(decimal_places=8, max_digits=13)),
                ('longitude', models.DecimalField(decimal_places=8, max_digits=13)),
                ('stadsdeel', models.CharField(db_index=True, max_length=1, null=True)),
                ('buurtcombinatie', models.CharField(db_index=True, max_length=3, null=True)),
                ('buurtcode', models.CharField(db_index=True, max_length=4, null=True)),
                ('sperscode', models.CharField(max_length=15)),
                ('qualcode', models.CharField(max_length=35, null=True)),
                ('ff_df', models.CharField(max_length=15, null=True)),
                ('nha_nr', models.IntegerField(null=True)),
                ('nha_hoogte', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
                ('uitval_nachtrun', models.CharField(max_length=8, null=True)),
                ('geometrie', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326)),
                ('geometrie_rd', django.contrib.gis.db.models.fields.PointField(null=True, srid=28992)),
                ('parkeervak_id', models.CharField(db_index=True, max_length=15, null=True)),
                ('parkeervak_soort', models.CharField(max_length=15, null=True)),
                ('bgt_wegdeel', models.CharField(db_index=True, max_length=38, null=True)),
                ('bgt_wegdeel_functie', models.CharField(db_index=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WegDeel',
            fields=[
                ('id', models.CharField(max_length=38, primary_key=True, serialize=False)),
                ('bgt_functie', models.CharField(max_length=200)),
                ('geometrie', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
        ),
    ]
