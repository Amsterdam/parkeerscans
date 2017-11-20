from random import uniform
import datetime

# import string

# Packages
from django.contrib.gis.geos import Point
import factory
# import faker
from factory import fuzzy

from datapunt_api.bbox import BBOX
from metingen import models


UTC = datetime.timezone.utc

lat1, lon1, lat2, lon2 = BBOX


class ScanFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Scan

    scan_id = fuzzy.FuzzyInteger(0)
    latitude = lat1
    longitude = lon1

    scan_moment = fuzzy.FuzzyDateTime(
            datetime.datetime(2017, 1, 1, tzinfo=UTC))

    parkeervak_id = fuzzy.FuzzyInteger(0, 100)
    bgt_wegdeel = fuzzy.FuzzyInteger(222, 234)

    geometrie = Point(
        uniform(lon1, lon2),
        uniform(lat1, lat2), srid=4326)
