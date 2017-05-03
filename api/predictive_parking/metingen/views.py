from rest_framework.response import Response

from rest_framework import viewsets, metadata

from datapunt import rest

from . import serializers
from . import models


class MetingenViewSet(rest.DatapuntViewSet):
    """
    Alle scan metingen

    - scan_id
    - scan_moment
    - device_id -  unieke device id / auto id
    - scan_source - auto of pda

    - buurtcode - bag GGW code
    - sperscode - (vergunning..)
    - qualcode- status / kwaliteit
    - nha_nr - naheffings_nummer
    - nha_hoogte - geldboete
    - uitval_nachtrun - nachtelijke correctie

    """

    queryset = models.Scan.objects.order_by('id')

    serializer_class = serializers.ScanList
    serializers_class_detail = serializers.Scan

    filter_fields = (
        'scan_moment',
        'device_id',
        'scan_source',
        'nha_hoogte',
        'nha_nr',
        'qualcode',
        'buurtcode',
        'sperscode',
        'parkeervak_id',
        'parkeervak_soort',
        'bgt_wegdeel',
        'bgt_wegdeel_functie',
    )

    ordering = ('scan_id')


def valid_bbox(bbox):
    """
    """
    bbox = bbox.split(',')

    if not len(bbox) == 4:
        return

    try:
        bbox = map(float, bbox)
    except ValueError:
        return

    return bbox


#class AggFilter(filters.BaseFilterBackend):
#    """
#    """
#    pass
#

class AggregationViewSet(viewsets.ViewSet):
    """
    Given bounding box  `bbox` return aggregations
    of wegdelen / vakken derived from scandata.
    """

    def list(self, request):

        if 'bbox' not in request.query_params:
            return Response([])

        bbox = request.query_params['bbox']

        bbox = valid_bbox(bbox)

        if not bbox:
            return Response(['bbox invalid'])

        lat1, lon1, lat2, lon2 = bbox

        return Response([lat1, lon1, lat2, lon2])

    def get_aggregations(self, bbox):
        """
        Given bbox find
        """
        pass


