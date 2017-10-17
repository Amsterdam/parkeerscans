from django.shortcuts import render

from . import serializers
from . import models

from datapunt import rest


class RoadOccupationViewSet(rest.DatapuntViewSet):
    """
    Geometrie / gebieden met parkeerkans informatie
    """

    queryset = models.RoadOccupation.objects.all()

    serializer_class = serializers.RoadOccupation

    filter_fields = (
        'bgt_id',

        'weekdag',
        'uur',
        'maand',
        'buurt',

        'fiscale_vakken',
        'bezettingsgraad',
    )

    # ordering = ('naam', 'weekdag', 'uur')
