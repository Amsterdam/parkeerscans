from __future__ import unicode_literals

from django.db import models

from django.contrib.gis.db import models as geo
# Create your models here.


class Parkeervak(models.Model):
    """
    Een parkeervak met relatie naar wegdeel WGS84
    """
    id = models.CharField(primary_key=True, max_length=30)
    straatnaam = models.CharField(db_index=True, max_length=300)
    soort = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    aantal = models.IntegerField()
    geometrie = geo.MultiPolygonField(srid=4326)
    point = geo.PointField(srid=4326, null=True)

    # wegdelen
    bgt_wegdeel = models.CharField(
        null=True, db_index=True, max_length=38)

    bgt_wegdeel_functie = models.CharField(
       null=True, db_index=True, max_length=25)

    buurt = models.CharField(
        null=True, db_index=True, max_length=4)

    # count indication of scans of last month
    # used to cleanup / find errors in dataset
    scan_count = models.IntegerField(null=True)


class WegDeel(models.Model):
    """
    Valide wegdelen die mogelijk een link kunnen hebben met een parkeervak
    geometrie in WGS84
    """
    id = models.AutoField(primary_key=True)
    # id = models.CharField(primary_key=True, max_length=38)
    bgt_id = models.CharField(db_index=True, max_length=38)
    bgt_functie = models.CharField(max_length=25)
    geometrie = geo.MultiPolygonField(srid=4326)
    vakken = models.IntegerField(null=True)
    fiscale_vakken = models.IntegerField(null=True)

    # count indication of scans of last month
    # used to cleanup / find errors in dataset
    scan_count = models.IntegerField(null=True)


class Buurt(models.Model):
    """
    Buurt
    """
    id = models.CharField(primary_key=True, max_length=14)
    code = models.CharField(db_index=True, max_length=4)
    naam = models.CharField(max_length=40)
    geometrie = geo.MultiPolygonField(srid=4326)
    vakken = models.IntegerField(null=True)
    fiscale_vakken = models.IntegerField(null=True)
