from rest_framework_gis.fields import GeometryField

from datapunt import rest

from . import models


class WegDeelList(rest.HALSerializer):

    dataset = 'wegdelen'

    # _display = rest.DisplayField()

    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            # '_display',
            'id',
            'vakken',
            'scan_count',
        )


class WegDeel(rest.HALSerializer):

    dataset = 'wegdelen'

    geometrie = rest.MultipleGeometryField()

    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            'id',
            'vakken',
            'fiscale_vakken',
            'scan_count',
            'bgt_functie',

            'geometrie',
        )


class ParkeerVakList(rest.HALSerializer):

    class Meta(object):
        model = models.Parkeervak

        fields = (
            'id',
            'aantal',
            'point',
        )


class ParkeerVak(rest.HALSerializer):

    geometrie = rest.MultipleGeometryField()

    class Meta(object):
        model = models.Parkeervak

        fields = (
            'id',
            'aantal',
            'straatnaam',
            'soort',
            'type',
            'aantal',
            'geometrie',
            'bgt_functie',
            # should be related field!!
            'bgt_wegdeel',
            'buurt',

            'scan_count',
        )


