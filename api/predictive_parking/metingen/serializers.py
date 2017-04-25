from rest_framework import serializers

from rest_framework_gis.fields import GeometryField

from datapunt import rest

from . import models

# from rest_framework.reverse import reverse


class Scan(rest.HALSerializer):

    dataset = 'scans'

    _display = rest.DisplayField()

    geometrie = GeometryField()

    verwachte_bezettingsgraad = serializers.DecimalField(
        max_digits=5,
        decimal_places=2)

    # group_geometrie = GeometryField()

    class Meta(object):
        model = models.Scan

        fields = (
            '_links',
            '_display',
            'scan_moment',
            'scan_source',
            'parkeervak_id',
            'parkeervak_soort',

            'weekdag',
            'uur',
            'buurtcode',
            'sperscode',
            'qualcode',

            'bgt_wegdeel',
            'bgt_wegdeel_functie',

            'nha_hoogte',
            'nha_nr',

            'geometrie',
        )
