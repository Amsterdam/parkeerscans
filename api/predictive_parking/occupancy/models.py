"""
OIS model parkeerkans uitkomsten
"""

from django.contrib.gis.db import models
from wegdelen.models import WegDeel


MONTHS = (
    (0, 'Jan'),
    (1, 'Feb'),
    (2, 'Mar'),
    (3, 'Apr'),
    (4, 'May'),
    (5, 'Jun'),
    (6, 'Jul'),
    (7, 'Aug'),
    (8, 'Sep'),
    (9, 'Okt'),
    (10, 'Nov'),
    (11, 'Dec'),
)

DAYS = (
    (0, 'Ma'),
    (1, 'Tu'),
    (2, 'We'),
    (3, 'Th'),
    (4, 'Fr'),
    (5, 'Sa'),
    (6, 'Su'),
)


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

    # iso weeknumber
    week = models.IntegerField(blank=False, null=True)

    status = models.IntegerField(blank=True, null=True)
    # buurt = models.CharField(db_index=True, null=True, max_length=4, )
    qualcode = models.CharField(blank=True, null=True, max_length=20)
    sperscode = models.CharField(blank=True, null=True, max_length=20)

    def _name(self):

        month2 = self.month2
        if month2 is None:
            month2 = self.month1

        year2 = self.year2 or self.year1
        day2 = self.day2 or self.day1

        s = self

        m = MONTHS
        d = DAYS

        code = self.qualcode or ''

        return \
            f'{s.year1}:{year2}:{m[s.month1][1]}:{m[month2][1]}:' + \
            f'{d[s.day1][1]}:{d[day2][1]}:{s.hour1:02}:{s.hour2:02}' + \
            f'{code}'

    def __repr__(self):
        return 'Selection: ' + self._name()

    def view_name(self):
        view_name = self._name()
        view_name = view_name.replace(':', '_')
        return view_name


class RoadOccupancy(models.Model):
    """
    Wegdeel parkeerdruk
    """
    id = models.AutoField(primary_key=True)
    bgt_id = models.CharField(db_index=True, max_length=38)
    # geometrie = models.GeometryField(blank=True, null=True, db_index=True)

    selection = models.ForeignKey(
        Selection, null=True, on_delete=models.CASCADE)
    wegdeel = models.ForeignKey(
        WegDeel, null=True, on_delete=models.CASCADE)

    # fiscale_vakken = models.IntegerField(blank=True, null=True)
    occupancy = models.FloatField(blank=True, null=True)
    max_occupancy = models.IntegerField(blank=True, null=True)
    min_occupancy = models.IntegerField(blank=True, null=True)
    std_occupancy = models.IntegerField(blank=True, null=True)
    days = models.IntegerField(blank=True, null=True)
    unique_scans = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (("bgt_id", "selection"),)


class BuurtOccupancy(models.Model):
    """
    Buurt
    """
    id = models.CharField(primary_key=True, max_length=14)
    code = models.CharField(db_index=True, max_length=4)
    naam = models.CharField(max_length=40)
    geometrie = models.MultiPolygonField(srid=4326)

    vakken = models.IntegerField(null=True)
    fiscale_vakken = models.IntegerField(null=True)

    selection = models.ForeignKey(
        Selection, null=True, on_delete=models.CASCADE)

    occupancy = models.FloatField(blank=True, null=True)
