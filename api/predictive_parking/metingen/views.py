"""
Collect aggregation information about roadparts / wegdelen.
given a bounding box

"""
import logging
# import sys
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
# from rest_framework.compat import coreapi
# from rest_framework.compat import coreschema

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
    # filter_backends = [MetingenFilter]

    ordering = ('scan_id')


def valid_bbox(bboxp):
    """
    Check if bbox is a valid bounding box
    """
    bbox = bboxp.split(',')
    err = None

    # check if we got 4 parametes
    if not len(bbox) == 4:
        return [], "wrong numer of arguments (lon, lat, lon, lat)"

    # check if we got floats
    try:
        bbox = [float(f) for f in bbox]
    except ValueError:
        return [], "Did not recieve floats"

    # max bbox sizes from mapserver
    # RD  EXTENT      100000    450000   150000 500000
    # WGS             52.03560, 4.58565  52.48769, 5.31360
    lat_min = 52.03560
    lat_max = 52.48769
    lon_min = 4.58565
    lon_max = 5.31360

    # check if coorinates are withing amsterdam
    # lat1, lon1, lat2, lon2 = bbox

    # bbox given by leaflet
    lon1, lat1, lon2, lat2 = bbox

    if not lat_max >= lat1 >= lat_min:
        err = f"lat not within max bbox {lat_max} > {lat1} > {lat_min}"

    if not lat_max >= lat2 >= lat_min:
        err = f"lat not within max bbox {lat_max} > {lat2} > {lat_min}"

    if not lon_max >= lon2 >= lon_min:
        err = f"lon not within max bbox {lon_max} > {lon2} > {lon_min}"

    if not lon_max >= lon1 >= lon_min:
        err = f"lon not within max bbox {lon_max} > {lon1} > {lon_min}"

    # this is how the code expects the bbox
    bbox = [lat1, lon1, lat2, lon2]

    return bbox, err


def determine_bbox(request):
    """
    Create a bounding box if it is given with the request.
    """

    err = "invalid bbox given"

    if 'bbox' not in request.query_params:
        # set default value
        return BBOX, None

    bboxp = request.query_params['bbox']
    bbox, err = valid_bbox(bboxp)

    if err:
        return None, err

    return bbox, err


def collect_wegdelen(elk_response):
    """
    collect all wegdelen ids
    """
    wegdelen = {}

    aggs = elk_response.get('aggregations')

    if not aggs:
        return {}, "no results.."

    day_buckets = aggs.get('scan_by_date')['buckets']

    for data in day_buckets.values():
        for wegdeel in data["wegdeel"]["buckets"]:
            wegdelen[wegdeel['key']] = {}

    return wegdelen, None


def proces_single_date(date: str, data: dict, wegdelen: dict):
    """
    For each date we get cardinality by hour

    Average the cardinality
    """

    for b_wegdeel in data['wegdeel']['buckets']:

        scans = b_wegdeel['doc_count']
        # update how many scans have been totally for this wegdeel

        key = b_wegdeel['key']

        db_wegdeel = wegdelen[key]

        capacity = db_wegdeel.get('total_vakken')

        db_wegdeel['unique_scans'] = db_wegdeel.setdefault(
            'unique_scans', 0) + scans

        # update how many days this road is observed
        db_wegdeel['days_seen'] = db_wegdeel.setdefault('days_seen', 0) + 1

        c_vakken = db_wegdeel.setdefault('cardinal_vakken_by_day', [])

        # update distinct vakken for date hour
        date_data = []

        for hour_d in b_wegdeel['hour']['buckets']:
            hour = hour_d['key']
            # h_scans = hour_d['doc_count']
            cardinal_vakken = hour_d['vakken']['value']
            if capacity:
                bezetting = int(cardinal_vakken / capacity * 100)
            else:
                bezetting = 0

            date_data.append([hour, bezetting])

        date_data.sort()

        c_vakken.append((date, date_data))


def build_wegdelen_data(elk_response: dict, wegdelen: dict):
    """
    Enrich wegdelen data with aggregated counts
    from elasticsearch.
    """
    # for each date we get some statistics
    date_buckets = elk_response['aggregations']['scan_by_date']['buckets']
    for date, data in date_buckets.items():

        proces_single_date(date, data, wegdelen)

    return wegdelen


def calculate_average_occupation(wegdeel, day_data):
    """
    From days and hours messured of a wegdeel
    give back the occupation
    """

    result_list = []

    for _date, hour_measurements in day_data:
        for _hour, percentage in hour_measurements:
            result_list.append(percentage)

    wegdeel['occupation'] = None

    if result_list:
        wegdeel['occupation'] = sum(result_list) / len(result_list)


def calculate_occupation(wegdelen, query_params):
    """
    calculate "bezetting"

    wegdelen zijn dict objecten met database
    elastic data/tellingen
    """
    explain = 'explain' in query_params

    for _k, wegd in wegdelen.items():

        if not wegd.get('total_vakken'):
            del wegd['cardinal_vakken_by_day']
            continue

        # lookup the stored counts by date and hour
        day_data = wegd['cardinal_vakken_by_day']

        calculate_average_occupation(wegd, day_data)

        if not explain:
            del wegd['cardinal_vakken_by_day']

    return wegdelen


class WegdelenAggregationViewSet(viewsets.ViewSet):
    """
    Given bounding box  `bbox` return aggregations
    of wegdelen / vakken derived from scandata with a
    'occupation' value. The value is determined by how many different
    parking spots where seen divided by the maximum capacity
    according the parking map/ parkeerkaart

    using elasticsearch.

    Parameter filter options
    =======

    add '?explain' parameter so see more details about calculation


        max-boundaties bounding-box. (groot Amsterdam)

                  4.58565,  52.03560,  5.31360, 52.48769,
        bbox      bottom,       left,      top,    right

        hour            [0 .. 23]
        hour_gte        [0 .. 23]
        hour_lte        [0 .. 23]
        minute_gte      [0 .. 59]
        minute_lte      [0 .. 59]
        day             [0 ..  6]
        day_gte         [0 ..  6]
        day_lte         [0 ..  6]
        month           [0 .. 11]
        wegdelen_size   [1 .. 190]           # amount of wegdelen to ask

        You can use date-math on date fields:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math

        date_gte        [2017, 2016-11-1]   # greater then equal
        date_lte        [2018, 2016-11-1]   # less then equal

        stadsdeel       [A ..]
        buurtcode       [A04a ..]
        buurtcombinatie [A04 ..]
        year            [2015.. 2024]
        bgt_wegdeel     [wegdeelid]
        qualcode        [
                            BEWONERP
                            BETAALDP
                            BEDRIJFP
                            STADSBREED
                            DOUBLESCAN
                            DISTANCE
                            ANPRERROR
                            TIMEOUT
                            DOUBLEPCN
                            TIMEOUT-PERMITCHECKER
                            BEZOEKP
                        ]

        sperscode       [
                            PermittedPRDB
                            Skipped
                            UnPermitted
                            NotFound
                            Exception
                            Suspect
                            PermittedHH
                        ]

        !! NOTE !!

        Default filter is current day and time.


    Response explanation
    =========

        {
            selection: {
               selection criteria from parameters or default
               default is current day and time for 2017
            },
            wegdelen: {
                "wegdeelID": {
                    totalvakken: unique vakken for wegdeel
                    occupation: xx
                    wegdeelDataX: ..
                    wegdeelDataFoo: ..
                }
            }
        }


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

        # clean client input
        cleaned_data, err = queries.clean_parameter_data(request)

        if err:
            return Response([f"invalid parameter {err}"], status=400)

        # get filter / must queries parts for elasti
        must = queries.build_must_queries(cleaned_data)

        # get aggregations from elastic
        wegdelen_size = cleaned_data.get('wegdelen_size', 150)
        elk_response, err = self.do_wegdelen_search(
            bbox, must, wegdelen_size=wegdelen_size)

        if settings.DEBUG:
            # Print elk response to console
            # print(json.dumps(elk_response, indent=4))
            # return Response(elk_response)
            pass

        if err:
            return Response([err], status=500)

        # collect all wegdelen id's in elastic response
        wegdelen, err = collect_wegdelen(elk_response)

        if err:
            return Response([err], status=400)

        # find and collect wegdelen meta data from DB.
        load_db_wegdelen(bbox, wegdelen)

        # now we have elastic data and database date to
        # calculate bezetting
        wegdelen_data = build_wegdelen_data(elk_response, wegdelen)

        wegdelen_data = calculate_occupation(
            wegdelen_data, request.query_params)

        return Response({
            'selection': cleaned_data,
            'wegdelen': wegdelen_data
        })

    def do_wegdelen_search(self, bbox, must=(), wegdelen_size=90):
        """
        Given bbox find

        - distinct wegdelen seen
        - distinct vakken seen for each wegdeel with counts
        """

        elk_q = queries.build_wegdeel_query(bbox, must, wegdelen_size)

        build_q = json.loads(elk_q)
        # log.debug(json.dumps(build_q, indent=4))

        try:
            result = ELK_CLIENT.search(
                index="scans*", size=0,
                timeout="1m", body=elk_q)
        except Exception as exeption:   # pylint: disable=broad-except
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

    db_wegdelen = wd_qs.filter(bgt_id__in=wegdelen.keys())

    for wegdeel in db_wegdelen:
        wegdelen[wegdeel.bgt_id].update({
            # 'bgt_functie': wegdeel.bgt_functie,
            # 'total_vakken': wegdeel.vakken,
            'total_vakken': wegdeel.fiscale_vakken,
            # NOT EFFICIENT !
            # 'geometry': json.loads(wegdeel.geometrie.json),
            # 'fiscaal': wegdeel.fiscale_vakken,
        })

    # log.debug('WEGDELEN %s' % wd_qs.count())


class VakkenAggregationViewSet(viewsets.ViewSet):
    """
    Return parkeervakken ordered by count
    """

    def list(self, request):
        """
        Show scan counts of parkingspot / vakken in given bbox
        """

        err = None

        bbox, err = determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox}"], status=400)

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
