from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from datapunt_api.serializers import MultipleGeometryField

from datapunt_api import rest

from . import models


class WegDeelList(rest.HALSerializer):

    dataset = 'wegdelen'

    _display = rest.DisplayField()



    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            '_display',
            'id',
            'vakken',
            'scan_count',
        )

    def get_selection(self, obj):
        return str(obj)


class WegDeel(rest.HALSerializer):

    dataset = 'wegdelen'

    _display = rest.DisplayField()

    geometrie = MultipleGeometryField()

    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            'id',
            '_display',
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
            '_links',
            'aantal',
            'point',
        )


class ParkeerVak(rest.HALSerializer):

    geometrie = MultipleGeometryField()

    class Meta(object):
        model = models.Parkeervak

        fields = (
            'id',
            '_links',
            'aantal',
            'straatnaam',
            'soort',
            'type',
            'aantal',
            'geometrie',
            # should be related field!!
            'bgt_wegdeel',
            'buurt',

            'scan_count',
        )
