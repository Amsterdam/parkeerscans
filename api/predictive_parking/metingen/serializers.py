from rest_framework_gis.fields import GeometryField

from datapunt import rest

from . import models

# from rest_framework.reverse import reverse


class ScanList(rest.HALSerializer):

    dataset = 'scans'

    _display = rest.DisplayField()

    class Meta(object):
        model = models.Scan

        fields = (
            '_links',
            '_display',
            'scan_moment',
            'parkeervak_id',
            'geometrie',
        )


class Scan(rest.HALSerializer):

    dataset = 'scans'

    _display = rest.DisplayField()

    geometrie = GeometryField()

    class Meta(object):
        model = models.Scan

        fields = (
            '_links',
            '_display',
            'scan_moment',
            'scan_source',
            'parkeervak_id',
            'parkeervak_soort',

            'buurtcode',
            'sperscode',
            'qualcode',

            'bgt_wegdeel',
            'bgt_wegdeel_functie',

            'nha_hoogte',
            'nha_nr',

            'geometrie',
        )
