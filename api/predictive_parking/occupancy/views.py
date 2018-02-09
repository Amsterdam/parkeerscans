# from django.shortcuts import render
import logging
import datetime

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

from .scrape_api import hour_range


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
        """ return some help information in filter form """
        return "filter using bbbox=4.58565,52.03560,5.31360,52.48769"


def fitting_selections() -> list:
    """
    Given the current time return fitting selection option

    from specific to less specific
    we will always find a somehwat fitting selection
    """

    delta = datetime.timedelta(days=100)
    now = datetime.datetime.now()
    before = now - delta

    hour = now.hour

    week1 = before.isocalendar()[1]
    week2 = now.isocalendar()[1]

    day1 = now.weekday()

    hour1 = now.hour
    hour2 = now.hour + 2

    # match hour with selection hour ranges
    for min_hour, max_hour in hour_range:
        if min_hour <= hour <= max_hour:
            hour1 = min_hour
            hour2 = max_hour
            break

    log.debug([hour1, hour2, day1, week1, week2])

    x_selections = models.Selection.objects.exclude(
            qualcode='BETAALDP')

    x_selections = x_selections.filter(status=1)

    options = [
        # find exact day
        x_selections.filter(
            day1,
            hour1=hour1, hour2=hour2,
        ),

        # find  day range
        x_selections.filter(
            day1_gte=day1, day2_lte=day1,
            hour1_gte=hour1, hour2_lte=hour2,
        ),

        # find hour range in week
        x_selections.filter(
            day1=0, day2=6,
            hour1=hour1, hour2=hour2,
        ),

        # find a week
        x_selections.filter(
            day1=0, day2=6,
        ),
    ]

    for option in options:
        log.debug(option.count())

    return options


def get_wegdelen(occupancy_qs, bbox_values):
    """
    retrieve wegdelen within bbox
    """
    lat1, lon1, lat2, lon2 = bbox_values

    poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

    wd_qs = occupancy_qs.filter(
        Q(**{"wegdeel__geometrie__overlaps": poly_bbox}))

    print(wd_qs.count())

    db_wegdelen = wd_qs.filter(wegdeel__vakken__gte=1)

    print(db_wegdelen.count())

    # return db_wegdelen
    return wd_qs


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
        """ not used """
        pass

    def list(self, request):
        """
        List the occupancy numbers.

        max 200 roadparts are taken
        """

        bbox_values, err = bbox.determine_bbox(request)

        # WEEKEND, WEEKDAY, DAYRANGE

        if err:
            return Response([f"bbox invalid {err}:{bbox_values}"], status=400)

        selections = fitting_selections()

        for option in selections:

            occupancy_numbers = models.RoadOccupancy.objects.filter(
                selection=option.id).select_related('wegdeel')

            if occupancy_numbers.count():
                # we find some roadparts matching
                log.debug(occupancy_numbers.count())
                break

        wegdelen = get_wegdelen(occupancy_numbers, bbox_values)

        log.debug('Roadparts found %d', wegdelen.count())

        occupancy = []

        for one_road in wegdelen[:100]:
            occupancy.append(one_road.occupancy)

        avg_occupancy = 1

        if sum(occupancy) == 0:
            avg_occupancy = -1
        else:
            avg_occupancy = sum(occupancy) / float(len(occupancy))

        result = [
            {
                'roadparts': wegdelen.count(),
                'occupancy': avg_occupancy,
                'bbox': bbox_values

            }
        ]
        # show found numbers (debug)
        status = 200
        result.extend(occupancy)
        if not occupancy:
            result[0]['status'] = 'oops something went wrong'
            status = 404

        return Response(result, status)
