from __future__ import unicode_literals

from django.db import models

from django.contrib.gis.db import models as geo
# Create your models here.


class Scan(models.Model):
    """
    Een scan punt

    -'scan_id'          # niet altijd uniek..
    -'scan_moment',
    -'device_id',       # unieke device id / auto id
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

    scan_id = models.IntegerField()  # not unique!!
    scan_moment = models.DateTimeField(db_index=True)
    device_id = models.IntegerField(null=True)
    scan_source = models.CharField(max_length=15)

    afstand = models.CharField(null=True, max_length=1)

    latitude = models.DecimalField(max_digits=13, decimal_places=8, null=False)

    longitude = models.DecimalField(
        max_digits=13, decimal_places=8, null=False)

    # Helaas niet alles heeft een buurtcode..?
    stadsdeel = models.CharField(null=True, max_length=1)
    buurtcombinatie = models.CharField(null=True, max_length=3)
    buurtcode = models.CharField(null=True, max_length=4)

    sperscode = models.CharField(max_length=15)

    qualcode = models.CharField(null=True, max_length=35)

    # Follow field, desk field
    ff_df = models.CharField(null=True, max_length=15)

    nha_nr = models.IntegerField(null=True)

    nha_hoogte = models.DecimalField(null=True, max_digits=6, decimal_places=3)
    uitval_nachtrun = models.CharField(null=True, max_length=8)

    geometrie = geo.PointField(null=True, srid=4326)
    geometrie_rd = geo.PointField(null=True, srid=28992)

    # parkeervak id ( rd coordinaten xy)
    parkeervak_id = models.CharField(db_index=True, null=True, max_length=15)
    # mulder / fiscaal / vrij
    parkeervak_soort = models.CharField(
        null=True, max_length=15)

    # wegdelen
    bgt_wegdeel = models.CharField(null=True, max_length=38)

    bgt_wegdeel_functie = models.CharField(null=True, max_length=25)

    objects = geo.GeoManager()


class ScanRaw(models.Model):
    """
    Een scan punt (zonder indexen)

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

    scan_id = models.IntegerField()  # not unique!!
    scan_moment = models.DateTimeField(db_index=True)
    device_id = models.IntegerField(null=True)
    scan_source = models.CharField(max_length=15)

    afstand = models.CharField(null=True, max_length=1)

    latitude = models.DecimalField(max_digits=13, decimal_places=8, null=False)

    longitude = models.DecimalField(
        max_digits=13, decimal_places=8, null=False)

    # Helaas niet alles heeft een buurtcode..?
    stadsdeel = models.CharField(null=True, max_length=1)
    buurtcombinatie = models.CharField(null=True, max_length=3)
    buurtcode = models.CharField(null=True, max_length=4)

    sperscode = models.CharField(max_length=15)

    qualcode = models.CharField(null=True, max_length=35)

    # Follow field, desk field
    ff_df = models.CharField(null=True, max_length=15)

    nha_nr = models.IntegerField(null=True)

    nha_hoogte = models.DecimalField(null=True, max_digits=6, decimal_places=3)
    uitval_nachtrun = models.CharField(null=True, max_length=8)

    geometrie = geo.PointField(null=True, srid=4326)
    geometrie_rd = geo.PointField(null=True, srid=28992)

    # parkeervak id ( rd coordinaten xy)
    parkeervak_id = models.CharField(null=True, max_length=15)
    # mulder / fiscaal / vrij
    parkeervak_soort = models.CharField(
        null=True, max_length=15)

    # wegdelen
    bgt_wegdeel = models.CharField(null=True, max_length=38)

    bgt_wegdeel_functie = models.CharField(null=True, max_length=25)

    objects = geo.GeoManager()
