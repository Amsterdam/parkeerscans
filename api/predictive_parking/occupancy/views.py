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
        'selection__year1',
        'selection__year2',
        'selection__month1',
        'selection__month2',
        'selection__day1',
        'selection__day2',
        'selection__hour1',
        'selection__hour2',
        'occupancy',
    )
