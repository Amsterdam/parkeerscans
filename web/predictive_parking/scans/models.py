from __future__ import unicode_literals

from django.db import models

from django.contrib.gis.db import models as geo
# Create your models here.


class Scan(models.Model):
    """
    Een scan punt

    -'scan_id'          # niet altijd uniek..
    -'scan_moment',
    -'scan_source',     # auto of pda
    -'longitude', 'latitude',
    -'buurtcode',       # GGW code
    -'afstand',         ..
    -'sperscode', (vergunning..)
    -'qualcode',        # status / kwaliteit
    -'ff_df',           # field of desk
    -'nha_nr', ignored? # naheffings_nummer
    -'nha_hoogte',      # geldboete
    -'uitval_nachtrun'  # nachtelijke correctie
    """

    scan_id = models.IntegerField()
    scan_moment = models.DateTimeField()
    scan_source = models.CharField(max_length=15)

    afstand = models.CharField(null=True, max_length=25)

    latitude = models.DecimalField(max_digits=13, decimal_places=8, null=False)
    longitude = models.DecimalField(
        max_digits=13, decimal_places=8, null=False)

    # helaas niet alles heeft een buurtcode..
    buurtcode = models.CharField(null=True, max_length=4)
    sperscode = models.CharField(max_length=15)

    qualcode = models.CharField(null=True, max_length=35)

    # follow field, desk field
    ff_df = models.CharField(null=True, max_length=15)

    nha_nr = models.IntegerField(null=True)

    nha_hoogte = models.DecimalField(null=True, max_digits=6, decimal_places=3)
    uitval_nachtrun = models.CharField(null=True, max_length=8)

    geometrie = geo.PointField(null=True, srid=4326)
    geometrie_rd = geo.PointField(null=True, srid=28992)

    objects = geo.GeoManager()
