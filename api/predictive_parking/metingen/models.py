"""

We define Scans and RawScans Models. these schema's are used
by the csv parser.

Scan model/table has more indexes then the RawScan Model/Table
to increase the speed of handling data.

"""

from __future__ import unicode_literals

import django

from django.db import models

from django.contrib.gis.db import models as geo

if django.VERSION < (2, 0):
    from django.contrib.gis.db.models import GeoManager
else:
    from django.db.models import Manager as GeoManager


class Scan(models.Model):
    """
    Een scan punt

    - scan_id           # niet uniek!
    - scan_moment
    - device_id         # unieke device id / auto id
    - scan_source       # auto of pda

    - buurtcode         # GGW code
    - sperscode         # (vergunning..)
    - qualcode          # status / kwaliteit
    - ff_df             # field of desk
    - nha_nr            # naheffings_nummer
    - nha_hoogte        # geldboete
    - uitval_nachtrun   # nachtelijke correctie
    - parkingbag_distance # afstand tot parkeervak
    - gps_vehicle       # gps_car
    - gps_plate         #
    - gps_scandevice    #
    - location_parking_bay # parkeervak geo / id
    - parking_bay_angle
    - reliability_gps
    - reliability_ANPR
    - parkeerrechtid
    """

    # parkeervak id ( rd coordinaten xy)
    parkeervak_id = models.CharField(db_index=True, null=True, max_length=15)
    # mulder / fiscaal / vrij
    parkeervak_soort = models.CharField(
        null=True, max_length=15)

    # wegdelen
    bgt_wegdeel = models.CharField(null=True, max_length=38)

    bgt_wegdeel_functie = models.CharField(null=True, max_length=25)

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

    sperscode = models.CharField(max_length=15, null=True)

    qualcode = models.CharField(null=True, max_length=35)

    # Follow field, desk field
    ff_df = models.CharField(null=True, max_length=15)

    nha_nr = models.CharField(max_length=15, null=True)

    nha_hoogte = models.DecimalField(null=True, max_digits=6, decimal_places=3)
    uitval_nachtrun = models.CharField(null=True, max_length=8)

    # extra fields from 10-2017

    # afstand tot parkeervak
    parkingbay_distance = models.FloatField(null=True)
    # center point car
    gps_vehicle = models.CharField(max_length=15, null=True)
    gps_plate = geo.PointField(null=True, srid=4326)
    gps_scandevice = geo.PointField(null=True, srid=4326)

    location_parking_bay = models.CharField(null=True, max_length=15)
    # parking_bay_angle
    parkingbay_angle = models.FloatField(null=True)
    # reliability_gps
    reliability_gps = geo.PointField(null=True, srid=4326)

    # reliability_ANPR
    reliability_ANPR = models.FloatField(null=True)

    parkeerrecht_id = models.BigIntegerField(null=True)

    geometrie = geo.PointField(null=True, srid=4326)
    objects = GeoManager()

    def __str__(self):
        return f"{self.scan_id} - {self.parkeervak_id}"


class ScanRaw(models.Model):
    """
    Een scan punt (WITHOUT INDEXES) for fast loading of csv.
    """

    # parkeervak id ( no index )
    parkeervak_id = models.CharField(null=True, max_length=15)

    # mulder / fiscaal / vrij
    parkeervak_soort = models.CharField(
        null=True, max_length=15)

    # wegdelen
    bgt_wegdeel = models.CharField(null=True, max_length=38)

    bgt_wegdeel_functie = models.CharField(null=True, max_length=25)

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

    nha_nr = models.CharField(max_length=15, null=True)

    nha_hoogte = models.DecimalField(null=True, max_digits=6, decimal_places=3)
    uitval_nachtrun = models.CharField(null=True, max_length=8)

    # extra fields from 10-2017

    # afstand tot parkeervak
    parkingbay_distance = models.FloatField(null=True)
    # center point car
    gps_vehicle = models.CharField(max_length=15, null=True)
    gps_plate = geo.PointField(null=True, srid=4326)
    gps_scandevice = geo.PointField(null=True, srid=4326)

    location_parking_bay = models.CharField(null=True, max_length=15)
    # parking_bay_angle
    parkingbay_angle = models.FloatField(null=True)
    # reliability_gps
    reliability_gps = geo.PointField(null=True, srid=4326)
    # reliability_ANPR
    reliability_ANPR = models.FloatField(null=True)

    parkeerrecht_id = models.BigIntegerField(null=True)

    geometrie = geo.PointField(null=True, srid=4326)
    objects = GeoManager()
