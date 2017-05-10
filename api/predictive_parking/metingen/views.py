"""
Collect aggregation information about roadparts / wegdelen.
given a bounding box

"""
import logging
import sys
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

from django_filters.rest_framework.filterset import FilterSet
from django_filters.rest_framework import filters

from datapunt import rest

from metingen import serializers
from metingen import models
from metingen import queries

from wegdelen.models import WegDeel


log = logging.getLogger(__name__)

# default amstermdam bbox lon, lat, lon, lat

BBOX = [52.03560, 4.58565,
        52.48769, 5.31360]

ELK_CLIENT = Elasticsearch(
    settings.ELASTIC_SEARCH_HOSTS,
    raise_on_error=True,
    timeout=100
)


class MetingenFilter(FilterSet):
    """
    Filter metingen op bbox
    """

    bbox = filters.CharFilter(method="bbox_filter")

    class Meta(object):
        model = models.Scan

        fields = (
            'bbox',
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

    def box_filter(self, queryset, _filter_name, value):

        bbox, err = valid_bbox(value)

        if err:
            return queryset

        lat1, lon1, lat2, lon2 = bbox
        bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        return queryset.filter(
            Q(**{"geometrie__bboverlaps": bbox}))


class MetingenViewSet(rest.DatapuntViewSet):
    """
    Scan metingen.

    Dit is de brondata voor:

    https://acc.parkeren.data.amsterdam.nl/

    Het is bijzonder onefficient om hier direct mee te werken

        scan_id
        scan_moment
        device_id -  unieke device id / auto id
        scan_source - auto of pda

        buurtcode - bag GGW code
        sperscode - (vergunning..)
        qualcode- status / kwaliteit
        nha_nr - naheffings_nummer
        nha_hoogte - geldboete
        uitval_nachtrun - nachtelijke correctie

    """

    queryset = models.Scan.objects.order_by('id')

    serializer_class = serializers.ScanList
    serializer_detail_class = serializers.Scan

    filter_class = MetingenFilter

    ordering = ('scan_id')


def valid_bbox(bboxp):
    """
    Check if bbox is a valid bounding box
    """
    bbox = bboxp.split(',')

    # check if we got 4 parametes
    if not len(bbox) == 4:
        return [], "wrong numer of arguments (lat, lon, lat, lon)"

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
    """
    Create a bounding box if it is given with the request.
    """

    bbox = []

    err = "invalid bbox given"

    if 'bbox' in request.query_params:
        bboxp = request.query_params['bbox']
        bbox, err = valid_bbox(bboxp)
    else:
        bbox = BBOX
        err = None

    return bbox, err


def collect_wegdelen(elk_response):
    """
    collect all wegdelen ids
    """
    wegdelen = {}

    date_buckets = elk_response['aggregations']['scan_by_date']['buckets']
    for _date, data in date_buckets.items():
        for wegdeel in data["wegdeel"]["buckets"]:
            wegdelen[wegdeel['key']] = {}

    return wegdelen


def build_wegdelen_data(elk_response: dict, wegdelen: dict):
    """
    Enrich wegdelen data
    """
    date_buckets = elk_response['aggregations']['scan_by_date']['buckets']
    for date, data in date_buckets.items():
        for b_wegdeel in data['wegdeel']['buckets']:
            key = b_wegdeel['key']
            db_wegdeel = wegdelen[key]
            # update how many days this road is observed
            db_wegdeel['days'] = db_wegdeel.setdefault('days', 0) + 1
            scans = b_wegdeel['doc_count']
            # update how many scans have been totally for this wegdeel
            db_wegdeel['scans'] = db_wegdeel.setdefault('scans', 0) + scans
            # update distinct vakken for date
            cardinal_vakken = b_wegdeel['vakken']['value']

            c_vakken = db_wegdeel.setdefault('cardinal_vakken', [])
            c_vakken.append((date, cardinal_vakken))

    return wegdelen


def calculate_pressure(wegdelen):
    """
    calculate "bezetting"

    wegdelen zijn dict objecten met database en elastic data/tellingen
    """

    for _k, wegd in wegdelen.items():
        totaal_gezien = sum([c for _, c in wegd['cardinal_vakken']])

        if wegd.get('totaal_vakken'):
            totaal_mogelijk = wegd['totaal_vakken'] * wegd['days']
            bezetting = float(totaal_gezien) / float(totaal_mogelijk)
            wegd['bezetting'] = "%.2f" % (bezetting)
        else:
            wegd['bezetting'] = "fout"

        totaal_scans = float(wegd.get('scans', 1.0)) or 1
        days = wegd.get('days', 1.0) or 1
        vakken = wegd.get('totaal_vakken', 1.0) or 1
        wegd['~scan-momenten-dag'] = "%.2f" % (totaal_scans / days / vakken)


class WegdelenAggregationViewSet(viewsets.ViewSet):
    """
    Given bounding box  `bbox` return aggregations
    of wegdelen / vakken derived from scandata.

    using elasticsearch.


    list:
                  52.03560, 4.58565  52.48769, 5.31360
        bbox      bottom,      left,      top,   right

        hour      [0.. 23]
        hour_1    [0 .. 23]
        hour_2    [0 .. 23]
        minute_1  [0 .. 59]
        minute_2  [0 .. 59]
        day       [monday, tuesay..]
        month     [january, february, match..]
        stadsdeel [A ..]
        buurtcode
        year
        parkeervak_soort
        parkeervak_id
        bgt_wegdeel
        qualcode
        sperscode

    """

    def list(self, request):
        """
        List dates with wegdeelen and distinct vakken count
        combined with meta road information
        """

        must = []

        err = None

        bbox, err = determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox}"], status=400)

        # get filter / must queries parts for elasti
        must, err = queries.build_must_queries(request)

        if err:
            return Response([f"invalid parameter {err}"], status=400)

        # get aggregations from elastic
        elk_response, err = self.do_wegdelen_search(bbox, must)

        if settings.DEBUG:
            # print(json.dumps(elk_response, indent=4))
            # return Response(elk_response)
            pass

        if err:
            return Response([err], status=400)

        # collect all wegdelen id's
        wegdelen = collect_wegdelen(elk_response)

        # find wegdelen from DB.
        load_db_wegdelen(bbox, wegdelen)

        wegdelen_data = build_wegdelen_data(elk_response, wegdelen)
        calculate_pressure(wegdelen_data)

        return Response(wegdelen_data)

    def do_wegdelen_search(self, bbox, must=[]):
        """
        Given bbox find

        - distinct wegdelen seen
        - distinct vakken seen for each wegdeel with counts

        """

        elk_q = queries.build_wegdeel_query(bbox, must)

        try:
            result = ELK_CLIENT.search(
                index="scans*", size=0,
                timeout="1m", body=elk_q)
        except Exception as exeption:
            log.debug(exeption)
            build_q = json.loads(elk_q)
            log.debug(json.dumps(build_q, indent=4))
            return [], 'elasticsearch query failed'

        return result, None


def load_db_wegdelen(bbox, wegdelen):
    """
    Given aggregation counts, determine "bezetting"
    """
    lat1, lon1, lat2, lon2 = bbox
    bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

    wd_qs = WegDeel.objects.all().filter(
        Q(**{"geometrie__bboverlaps": bbox}))

    db_wegdelen = wd_qs.filter(id__in=wegdelen.keys())

    for wegdeel in db_wegdelen:
        wegdelen[wegdeel.id].update({
            'bgt_functie': wegdeel.bgt_functie,
            'totaal_vakken': wegdeel.vakken,
            # NOT EFFICIENT !
            # 'geometry': json.loads(wegdeel.geometrie.json),
            'fiscaal': wegdeel.fiscale_vakken,
        })

    log.debug(wd_qs.count())
    # assert wegdelen


class VakkenAggregationViewSet(viewsets.ViewSet):
    """
    Return parkeervakken ordered by count
    """

    def list(self, request):
        """
        show counts of vakken in the bbox
        """

        err = None

        bbox, err = determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox}"])

        elk_response = self.get_aggregations(bbox)

        # count in involved scans
        count = elk_response.hits.total

        pv_elk = elk_response.aggregations['parkeervaken']

        parkeervakken = [(i['key'], i['doc_count']) for i in pv_elk]

        result = {
            'scancount': count,
            'vakken': parkeervakken,
        }

        return Response(result)

    def get_aggregations(self, bbox):
        """
        Given bbox find

        - distinct wegdelen seen
        """

        elk_q = queries.aggregation_query(bbox)

        search = elk_q.to_elasticsearch_object(ELK_CLIENT)

        search = self.add_agg_to_search(search)

        if settings.DEBUG:
            log.debug(json.dumps(search.to_dict(), indent=4))

        # result = search.execute(ignore_cache=ignore_cache)
        result = search.execute()

        return result

    def add_agg_to_search(self, search_object):
        """
        Find x most scanned spots
        """

        parkeervak_agg = A(
            'terms', field='parkeervak_id.keyword', size=2000)

        search_object.aggs.bucket('parkeervaken', parkeervak_agg)

        return search_object
