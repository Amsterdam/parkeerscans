# Create your views here.

from datapunt import rest

from . import models
from . import serializers


class WegdelenViewSet(rest.DatapuntViewSet):
    """
    Wegdelen

    Dit is de brondata voor:

    https://acc.parkeren.data.amsterdam.nl/

    """

    queryset = models.WegDeel.objects.order_by('id')

    serializer_class = serializers.WegDeelList
    serializer_detail_class = serializers.WegDeel

    lookup_value_regex = '[^/]+'

    filter_fields = (
        'vakken',
        'scan_count',
    )
    # filter_class = MetingenFilter


class VakkenViewSet(rest.DatapuntViewSet):
    """
    Parkeer Vakken

    Dit is de brondata voor:

    https://acc.parkeren.data.amsterdam.nl/

    """

    queryset = models.Parkeervak.objects.order_by('id')

    serializer_class = serializers.ParkeerVakList
    serializer_detail_class = serializers.ParkeerVak

    lookup_value_regex = '[^/]+'

    filter_fields = (
        'scan_count',
    )

