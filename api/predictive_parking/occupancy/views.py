from django.shortcuts import render

from . import serializers
from . import models

from datapunt import rest


class RoadOccupancyViewSet(rest.DatapuntViewSet):
    """
    Geometrie / gebieden met parkeerkans informatie
    """

    queryset = models.RoadOccupancy.objects.all()

    serializer_class = serializers.RoadOccupancy
    serializer_detail_class = serializers.RoadOccupancy

    filter_fields = (
        'bgt_id',

        #'weekdag',
        #'uur',
        #'maand',
        #'buurt',

        #'fiscale_vakken',
        #'bezettingsgraad',
    )

    # ordering = ('naam', 'weekdag', 'uur')
