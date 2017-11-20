# from django.shortcuts import render
import logging
from django.utils.encoding import force_text
from django.contrib.gis.geos import Polygon
from django.db.models import Q

# from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import viewsets

from rest_framework.compat import coreapi
from rest_framework.compat import coreschema

from datapunt_api import rest
from datapunt_api import bbox

from wegdelen.models import WegDeel

from . import serializers
from . import models

log = logging.getLogger(__name__)


class RoadOccupancyViewSet(rest.DatapuntViewSet):
    """
    Geometrie / gebieden met parkeerkans informatie
    """

    queryset = models.RoadOccupancy.objects.all()

    serializer_class = serializers.RoadOccupancyList
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


class BboxFilter(object):
    """
    OpenAPI doc for bbox filter
    """
    # bbox
    bbox_desc = """
                  4.58565,  52.03560,  5.31360, 52.48769,
        bbox      bottom,       left,      top,    right
    """

    def get_schema_fields(self, _view):
        """
        return Q parameter documentation
        """
        fields = [
            coreapi.Field(
                name='bbox',
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text('Bounding box.'),
                    description=force_text(self.bbox_desc)
                )
            )
        ]
        return fields

    def to_html(self, request, queryset, view):
        log.error('yay')
        return "filter using bbbox=4.58565,52.03560,5.31360,52.48769"


class OccupancyInBBOX(viewsets.ViewSet):
    """
    Get an occupancy number for a location in the city of Amsterdam.

    Given bounding box  `bbox` return average occupation
    of roadparts withing the given `bounding box`.

        max-boundaties bounding-box. (groot Amsterdam)

                  4.58565,  52.03560,  5.31360, 52.48769,
        bbox      bottom,       left,      top,    right


    The results are made possible by the scan measurements of
    the scan-cars.

    """
    filter_backends = [BboxFilter]

    def get_queryset(self):
        pass

    def get_wegdelen(self, occupancy_qs, bbox_values):
        """
        retrieve wegdelen within bbox
        """
        lat1, lon1, lat2, lon2 = bbox_values

        poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        wd_qs = occupancy_qs.filter(
            Q(**{"wegdeel__geometrie__bboverlaps": poly_bbox}))

        db_wegdelen = wd_qs.filter(wegdeel__vakken__gte=3)
        db_wegdelen = db_wegdelen.filter(wegdeel__scan_count__gte=100)

        return db_wegdelen

    def list(self, request):
        """
        List the occupancy numbers.

        max 200 roadparts are taken
        """
        bbox_values, err = bbox.determine_bbox(request)

        # WEEKEND, WEEKDAY, DAYRANGE

        if err:
            return Response([f"bbox invalid {err}:{bbox_values}"], status=400)

        done = 1

        selection = models.Selection.objects.filter(
                day1=0, day2=6, hour1=0, hour2=23,
                year1=2017, status=done).first()

        if not selection:
            return Response([f"selections are missing.."], status=500)

        occupancy_numbers = models.RoadOccupancy.objects.filter(
            selection=selection.id).select_related('wegdeel')

        wegdelen = self.get_wegdelen(occupancy_numbers, bbox_values)

        occupancy = []

        for wd in wegdelen[:100]:
            occupancy.append(wd.occupancy)

        result = [
            {
                'roadparts': wegdelen.count(),
                'occupation':  sum(occupancy) / float(len(occupancy)),
                'bbox': bbox_values

            }
        ]
        result.extend(occupancy)

        return Response(result)
