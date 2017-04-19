"""
OIS model parkeerkans uitkomsten
"""

from django.contrib.gis.db import models


class Mvp(models.Model):
    """
    Mvp model outputs
    """
    group_geometrie = models.GeometryField(blank=True, null=True)
    vollcode = models.CharField(max_length=4, blank=True, null=True)
    naam = models.CharField(max_length=40, blank=True, null=True)
    weekdag = models.FloatField(blank=True, null=True)
    uur = models.FloatField(blank=True, null=True)
    aantal_fiscale_vakken = models.BigIntegerField(blank=True, null=True)
    verwachte_bezettingsgraad = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True)
    parkeerkansindicatie = models.TextField(blank=True, null=True)
    betrouwbaarheid = models.FloatField(blank=True, null=True)

    class Meta:
        """This object is NOT managed by django and given"""
        managed = False
        db_table = 'mvp'
