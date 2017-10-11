"""
OIS model parkeerkans uitkomsten
"""

from django.contrib.gis.db import models


class Selection(models.Model):
    """
    Selections..
    """

    day1 = models.IntegerField(blank=False, null=False, db_index=True)
    day2 = models.IntegerField(blank=False, null=True, db_index=True)

    hour1 = models.IntegerField(blank=False, null=False, db_index=True)
    hour2 = models.IntegerField(blank=False, null=True, db_index=True)

    month1 = models.IntegerField(blank=False, null=False, db_index=True)
    month2 = models.IntegerField(blank=False, null=True, db_index=True)

    year1 = models.IntegerField(blank=False, null=False)
    year2 = models.IntegerField(blank=False, null=True)

    # buurt = models.CharField(db_index=True, null=True, max_length=4, )


class RoadOccupation(models.Model):
    """
    Wegdeel parkeerdruk
    """
    id = models.AutoField(primary_key=True)
    bgt_id = models.CharField(db_index=True, max_length=38)
    # geometrie = models.GeometryField(blank=True, null=True, db_index=True)

    selection = models.ForeignKey(Selection, null=True)

    # fiscale_vakken = models.IntegerField(blank=True, null=True)
    occupation = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = (("bgt_id", "selection"),)


class BuurtOccupation(models.Model):
    """
    Buurt
    """
    id = models.CharField(primary_key=True, max_length=14)
    code = models.CharField(db_index=True, max_length=4)
    naam = models.CharField(max_length=40)
    geometrie = models.MultiPolygonField(srid=4326)

    vakken = models.IntegerField(null=True)
    fiscale_vakken = models.IntegerField(null=True)

    selection = models.ForeignKey(Selection, null=True)

    occupation = models.FloatField(blank=True, null=True)
