from django.shortcuts import render

from . import serializers
from . import models

from datapunt import rest


class KansmodelViewSet(rest.DatapuntViewSet):
    """
    Raster data van OIS met parkeerkans berekeneningen
    per geometrie / raster.

    Per buurt is een kans berekening gedaan.

    Filteren kan op weekdag en uur en locatie.

    Geometrie / gebieden met parkeerkans informatie


    """

    queryset = models.Mvp.objects.all()

    serializer_class = serializers.Kansmodel

    filter_fields = (
        'naam', 'weekdag',
        'uur', 'aantal_fiscale_vakken')

    ordering = ('naam', 'weekdag', 'uur')
