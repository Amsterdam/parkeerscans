import logging
import json

from rest_framework import viewsets
from rest_framework.response import Response

from django.db.models import Q
from django.conf import settings
from django.contrib.gis.geos import Polygon


from elasticsearch import Elasticsearch
from elasticsearch_dsl import A

# from elasticsearch.exceptions import TransportError
# from elasticsearch_dsl import Search

from datapunt import rest

from metingen import serializers
from metingen import models
from metingen import queries

from wegdelen.models import WegDeel


log = logging.getLogger(__name__)

# default amstermdam bbox
BBOX = [52.03560, 4.58565,
        52.48769, 5.31360]

ELK_CLIENT = Elasticsearch(
    settings.ELASTIC_SEARCH_HOSTS,
    raise_on_error=True,
    timeout=100
)


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
    Check if bbox is a valid bounding box
    """
    bbox = bbox.split(',')

    # check if we got 4 parametes
    if not len(bbox) == 4:
        return [], "wrong numer of arguments"

    # check if we got floats
    try:
        bbox = map(float, bbox)
    except ValueError:
        return [], "Did not recieve floats"

    # max bbox sizes from mapserver
    # RD  EXTENT      100000    450000   150000 500000
    # WGS             52.03560, 4.58565  52.48769, 5.31360
    lat_min = 52.03560
    lat_max = 52.48769
    lon_max = 4.58565
    lon_min = 5.31360

    # check if coorinates are withing amsterdam
    lat1, lon1, lat2, lon2 = bbox

    if not lat_max > lat1 > lat_min:
        err = "lat not within max bbox"

    if not lat_max > lat2 > lat_min:
        err = "lat not within max bbox"

    if not lon_max > lon2 > lon_min:
        err = "lon not within max bbox"

    if not lon_max > lon1 > lon_min:
        err = "lon not within max bbox"

    return bbox, err


def determine_bbox(request):

    bbox = None

    err = "invalid bbox given"

    if 'bbox' in request.query_params:
        bbox = request.query_params['bbox']
        bbox, err = valid_bbox(bbox)
    else:
        bbox = BBOX
        err = None

    return bbox, err


class WegdelenAggregationViewSet(viewsets.ViewSet):
    """
    Given bounding box  `bbox` return aggregations
    of wegdelen / vakken derived from scandata.

    using elasticsearch.

    # BBOX   52.03560, 4.58565  52.48769, 5.31360

    parameters:

        bbox

        hours
        minutes
        weekdays
        days
        month
        stadsdeel
        buurtcode
        year
        qualcode
        sperscode
    """

    def list(self, request):

        err = None

        bbox, err = determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox}"])

        # find wegdelen from DB.
        wegdelen = self.get_wegdelen(bbox)

        # get aggregations from elastic
        elk_response = self.get_aggregations(bbox)

        # count in involved scans
        count = elk_response.hits.total

        if settings.DEBUG:
            self.debug_sample(elk_response)

        elk_wegdelen = elk_response.aggregations['wegdelen']

        wegdelen = {}

        for wegdeel in elk_wegdelen:
            # wegdeel.

            i = {
                "scan_count": wegdeel['doc_count'],
            }

            # parkeervak count.
            aggs = list(wegdeel)
            i['vakken'] = aggs[0]['value']

            wegdelen[wegdeel['key']] = i

        # merge wegdelen information from db
        self.combine(bbox, wegdelen)

        result = {
            'scancount': count,
            'wegdelen': wegdelen,
        }

        if settings.DEBUG:
            result['bbox'] = bbox
            result['scans'] = [h.to_dict() for h in elk_response.hits[:10]]

        return Response(result)

    def debug_sample(self, elk_response):
        """
        Show sample of aggregation
        """

        for agg in elk_response.aggregations:
            for item in agg['buckets'][:10]:
                print(item['key'], item['doc_count'])

    def get_aggregations(self, bbox):
        """
        Given bbox find

        - distinct wegdelen seen
        - distinct vakken seen for each wegdeel with counts

        """

        elk_q = queries.aggregation_query(bbox)

        search = elk_q.to_elasticsearch_object(ELK_CLIENT)

        search = self.add_agg_to_search(search)

        # result = search.execute(ignore_cache=ignore_cache)
        result = search.execute()

        return result

    def add_agg_to_search(self, search_object):
        """
        Add wegdelen and parkeervak aggregation
        to seach
        """
        wegdeel_agg = A(
            'terms', field='bgt_wegdeel.keyword', size=500)

        wegdeel_agg.bucket(
            'vakkken', 'cardinality', field='parkeervak_id.keyword')

        # wegdeel
        search_object.aggs.bucket('wegdelen', wegdeel_agg)

        log.debug(
            json.dumps(
                search_object.to_dict(), indent=4, sort_keys=True))

        return search_object

    def get_wegdelen(self, bbox):
        """
        Get all involved wegdelen within bounding box
        """
        assert bbox

        # do bbox query
        return []

    def combine(self, bbox, wegdelen):
        """
        Given aggregation counts, determine "bezetting"
        """
        lat1, lon1, lat2, lon2 = bbox

        print(bbox)

        bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        print(bbox)

        wd = WegDeel.objects.all().filter(
            Q(**{"geometrie__bboverlaps": bbox}))

        db_wegdelen = wd.filter(id__in=wegdelen.keys())

        for w in db_wegdelen:
            wegdelen[w.id].update({
                'bgt_functie': w.bgt_functie,
                'totaal_vakken': w.vakken,
                'fiscaal': w.fiscale_vakken,
            })
        print(wd.count())

        assert wegdelen

        return []


class VakkenAggregationViewSet(viewsets.ViewSet):
    """
    Return parkeervakken ordered by count
    """

    def list(self, request):

        err = None

        bbox, err = determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox}"])

        elk_response = self.get_aggregations(bbox)

        # count in involved scans
        count = elk_response.hits.total

        pv = elk_response.aggregations['parkeervaken']

        parkeervakken = [(i['key'], i['doc_count']) for i in pv]

        result = {
            'scancount': count,
            'vakken': parkeervakken,
        }

        if settings.DEBUG:
            result['bbox'] = bbox

        return Response(result)

    def get_aggregations(self, bbox):
        """
        Given bbox find

        - distinct wegdelen seen
        """

        elk_q = queries.aggregation_query(bbox)

        search = elk_q.to_elasticsearch_object(ELK_CLIENT)

        search = self.add_agg_to_search(search)

        # result = search.execute(ignore_cache=ignore_cache)
        result = search.execute()

        return result

    def add_agg_to_search(self, search_object):

        parkeervak_agg = A(
            'terms', field='parkeervak_id.keyword', size=2000)

        search_object.aggs.bucket('parkeervaken', parkeervak_agg)

        return search_object
