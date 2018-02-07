"""
OIS model parkeerkans uitkomsten
"""
import logging

from django.contrib.gis.db import models
from wegdelen.models import WegDeel

log = logging.getLogger(__name__)


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


def _range_repr(r1: int, r2: int, timestr=None) -> str:
    """
    Make reresentation of time range.

    month1-month2

    if r1, r2 are equal just return month1 / r1

    timestr are string representations of time.
    days, months, weeks if present return string 'jan' , 'feb'
    """

    if r1 is None:
        return

    if r2 is not None:
        if r1 == r2:

            if timestr:
                return f'{timestr[r1][1]}'

            return f'{r1}'

        if timestr:
            return f'{timestr[r1][1]}-{timestr[r2][1]}'

        return f'{r1}-{r2}'

    if timestr:
        return f'{timestr[r1][1]}'

    return '{r1}'


class Selection(models.Model):
    """
    Selections..
    """

    day1 = models.IntegerField(blank=False, null=False, db_index=True)
    day2 = models.IntegerField(blank=False, null=True, db_index=True)

    hour1 = models.IntegerField(blank=False, null=False, db_index=True)
    hour2 = models.IntegerField(blank=False, null=True, db_index=True)

    month1 = models.IntegerField(blank=False, null=True, db_index=True)
    month2 = models.IntegerField(blank=False, null=True, db_index=True)

    year1 = models.IntegerField(blank=False, null=False)
    year2 = models.IntegerField(blank=False, null=True)

    # iso weeknumber 0-52
    # week = models.IntegerField(blank=False, null=True)
    week1 = models.IntegerField(blank=False, null=True)
    week2 = models.IntegerField(blank=False, null=True)

    status = models.IntegerField(blank=True, null=True)
    # buurt = models.CharField(db_index=True, null=True, max_length=4, )
    qualcode = models.CharField(blank=True, null=True, max_length=20)
    sperscode = models.CharField(blank=True, null=True, max_length=20)

    def _name(self):

        month = _range_repr(self.month1, self.month2, MONTHS)
        day = _range_repr(self.day1, self.day2, DAYS)

        week = _range_repr(self.week1, self.week2)
        year = _range_repr(self.year1, self.year2)

        code = self.qualcode or ''
        s = self

        block = None

        if month is not None:
            block = month

        if week is not None:
            block = week

        if not block:
            log.error(
                '%s %s %s %s %s %s',
                self.year1, self.year2,
                self.month1, self.month2,
                self.week1, self.week2)
            log.error(self)

        # assert block

        return \
            f'{year}:{block}:' + \
            f'{day}:{s.hour1:02}:{s.hour2:02}' + \
            f'-{code}'

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
