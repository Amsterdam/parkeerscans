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

    status = models.IntegerField(blank=True, null=True)
    # buurt = models.CharField(db_index=True, null=True, max_length=4, )

    def _name(self):

        month2 = self.month2 or self.month1
        year2 = self.year2 or self.year1
        day2 = self.day2 or self.day1

        s = self

        return \
            f'{s.year1}:{year2}:{s.month1}:{month2}:' + \
            f'{s.day1}:{day2}:{s.hour1}:{s.hour2}'

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

    selection = models.ForeignKey(Selection, null=True)

    # fiscale_vakken = models.IntegerField(blank=True, null=True)
    occupancy = models.FloatField(blank=True, null=True)

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

    selection = models.ForeignKey(Selection, null=True)

    occupancy = models.FloatField(blank=True, null=True)
