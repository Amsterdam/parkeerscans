from rest_framework import serializers

from datapunt import rest

from . import models


class RoadOccupation(rest.HALSerializer):

    dataset = 'wegdeelbezetting'

    _display = rest.DisplayField()

    bezettingsgraad = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    geometrie = rest.MultipleGeometryField()

    class Meta(object):
        model = models.RoadOccupation

        fields = (
            '_links',
            '_display',

            'uur',
            'weekdag',
            'maand',
            'fiscale_vakken',
            'bezettingsgraad',
            'buurt',
            'geometrie',
        )
