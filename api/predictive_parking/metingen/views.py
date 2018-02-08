"""
Collect aggregation information about roadparts / wegdelen.
given a bounding box

"""
import logging
import statistics
import datetime
# import sys
import json

from rest_framework import viewsets
# from rest_framework import metadata
from rest_framework.response import Response

from django.db.models import Q
from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.utils.encoding import force_text


from elasticsearch import Elasticsearch
from elasticsearch_dsl import A

# from elasticsearch.exceptions import TransportError
# from elasticsearch_dsl import Search
from rest_framework.compat import coreapi
from rest_framework.compat import coreschema

from django_filters.rest_framework.filterset import FilterSet
from django_filters.rest_framework import filters

from datapunt_api import rest
from datapunt_api import bbox

from metingen import serializers
from metingen import models
from metingen import queries

from wegdelen.models import WegDeel


log = logging.getLogger(__name__)


ELK_CLIENT = Elasticsearch(
    settings.ELASTIC_SEARCH_HOSTS,
    raise_on_error=True,
    timeout=400
)


def get_all_indices():
    indices = ELK_CLIENT.indices.get('scans-*')
    keys = list(indices.keys())
    keys.sort()
    # log.debug(keys)
    # indices.sort()
    return keys


def extract_dates(indices):
    """
    create list with datetime-index tuples from indices
    """

    dates = []

    for indexname in indices:
        if '-' not in indexname:
            continue
        if not indexname.startswith('scans'):
            continue

        datepart = indexname.split('-')[1]

        try:
            year, month, day = datepart.split('.')
        except ValueError:
            log.exception('weird index?', indexname)
            continue

        dt = datetime.datetime(
            year=int(year), month=int(month), day=int(day))

        dates.append((dt, indexname))

    return dates


def meta_date_range_message(date_tuples: list):
    """
    Exctract a meta data information message from available
    indices
    """

    if not date_tuples:
        raise ValueError('no indices?')

    min_date = date_tuples[0][0]
    max_date = date_tuples[-1][0]

    year_min, month_min, day_min = min_date.year, min_date.month, min_date.day
    year_max, month_max, day_max = max_date.year, max_date.month, max_date.day

    date_range_information = dict(
        min=f'{year_min}:{month_min}:{day_min}',
        max=f'{year_max}:{month_max}:{day_max}'
    )

    return date_range_information


def determine_relevant_indices(params: dict) -> (str, dict, list):
    """
    Given year_gte, week_gte
    and year_lte, week_lte

    filter out irrelevant indices

    makes elastic more efficient.
    provide user with meta data information.

    Example:
        scans-2018.01.29
        scans-2017.12.29
        scans-2017.11.29
        scans-2017.10.29
    """
    err = None
    valid_indices = []
    indices = get_all_indices()
    date_tuples = extract_dates(indices)

    year_gte = params.get('year_gte')
    week_gte = params.get('week_gte')
    year_lte = params.get('year_lte')
    week_lte = params.get('week_lte')

    if not year_gte or not week_gte:
        # nothing todo.
        return None, params, indices

    if not year_lte or not week_lte:
        # nothing todo.
        return None, params, indices

    dt_gte = datetime.datetime(year=year_gte, month=1, day=1)
    weeks_gte = datetime.timedelta(weeks=week_gte)
    gte_date = dt_gte + weeks_gte

    dt_lte = datetime.datetime(year=year_lte, month=1, day=1)
    weeks_lte = datetime.timedelta(weeks=week_lte)
    week = datetime.timedelta(days=7)
    lte_date = dt_lte + weeks_lte + week

    for dt, indexname in date_tuples:
        if dt >= gte_date and dt < lte_date:
            valid_indices.append(indexname)
            log.debug(' ok  %s  %s  %s', gte_date, indexname, lte_date)
        else:
            log.debug('out  %s  %s  %s', gte_date, indexname, lte_date)

    date_range_information = meta_date_range_message(date_tuples)

    if not valid_indices:
        err = f"""
            No data available for given date range
            {date_range_information}
        """

        return err, params, []

    params['available_date_range'] = date_range_information

    return err, params, valid_indices


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

        bbox_values, err = bbox.valid_bbox(value)

        if err:
            return queryset

        lat1, lon1, lat2, lon2 = bbox_values
        poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

        return queryset.filter(
            Q(**{"geometrie__bboverlaps": poly_bbox}))


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


def collect_wegdelen(wegdelen: dict, elk_response: dict):
    """
    collect all wegdelen ids
    """

    aggs = elk_response.get('aggregations')

    if not aggs:
        return {}, "no results.."

    day_buckets = aggs.get('scan_by_date')['buckets']

    for data in day_buckets.values():
        for wegdeel in data["wegdeel"]["buckets"]:
            wegdelen[wegdeel['key']] = {}


def proces_single_day(date: str, data: dict, wegdelen: dict):
    """
    For each date / single day we get cardinality by hour

    Average the cardinality
    """

    for bucket_wegdeel in data['wegdeel']['buckets']:

        scans = bucket_wegdeel['doc_count']
        # update how many scans have been totally for this wegdeel

        key = bucket_wegdeel['key']
        db_wegdeel = wegdelen[key]
        capacity = db_wegdeel.get('total_vakken')
        db_wegdeel['unique_scans'] = db_wegdeel.setdefault(
            'unique_scans', 0) + scans

        # update how many days this road is observed
        db_wegdeel['days_seen'] = db_wegdeel.setdefault('days_seen', 0) + 1
        c_vakken = db_wegdeel.setdefault('cardinal_vakken_by_day', [])

        # update distinct vakken for date hour
        date_data = _calculate_occupancy_by_hour(bucket_wegdeel, capacity)
        c_vakken.append((date, date_data))


def _calculate_occupancy_by_hour(bucket_wegdeel: dict, capacity: int) -> list:

        date_data = []
        # calculate occupancy by hour
        for hour_d in bucket_wegdeel['hour']['buckets']:
            hour = hour_d['key']
            # h_scans = hour_d['doc_count']
            cardinal_vakken = hour_d['vakken']['value']

            if capacity:
                occupancy = int(cardinal_vakken / capacity * 100)
            else:
                occupancy = 0

            date_data.append([hour, occupancy])

        date_data.sort()

        return date_data


def build_wegdelen_data(all_responses: list, wegdelen: dict):
    """
    Enrich wegdelen data with aggregated counts
    from elasticsearch.
    """
    for elk_response in all_responses:
        # for each date we get some statistics
        date_buckets = elk_response['aggregations']['scan_by_date']['buckets']

        for date, data in date_buckets.items():
            proces_single_day(date, data, wegdelen)

    return wegdelen


def calculate_average_occupancy(wegdeel, day_data):
    """
    From days and hours messured of a wegdeel
    give back occupancy statistics
    """

    result_list = []
    _max = 0
    _min = 999
    _sum = 0
    _avg = 0

    # collect all occupancy's for each hour in day
    for _date, hour_measurements in day_data:
        for _hour, percentage in hour_measurements:
            result_list.append(percentage)
            if percentage > _max:
                _max = percentage
            elif percentage < _min:
                _min = percentage
            _sum += percentage

    wegdeel['avg_occupancy'] = None

    _len_results = len(result_list)

    # calculate the average occupancy.
    if result_list:
        _avg = _sum / _len_results
        wegdeel['avg_occupancy'] = round(_avg, 3)
        wegdeel['min_occupancy'] = _min
        wegdeel['max_occupancy'] = _max
        if _len_results > 1:
            wegdeel['std_occupancy'] = int(statistics.stdev(result_list))


def calculate_occupancy(wegdelen, query_params):
    """
    calculate "bezetting" / occupancy

    wegdelen are dict objects with database rows
    combined elastic data aggregations
    """
    explain = 'explain' in query_params

    for _k, wegd in wegdelen.items():

        if not wegd.get('total_vakken'):
            del wegd['cardinal_vakken_by_day']
            continue

        # lookup the stored counts by date and hour
        day_data = wegd['cardinal_vakken_by_day']

        calculate_average_occupancy(wegd, day_data)

        # remove the scan information by day!
        if not explain:
            del wegd['cardinal_vakken_by_day']

    return wegdelen


#  Disabled not suitable for public.
#  too detailed

#  minute_gte      [0 .. 59]
#  minute_lte      [0 .. 59]

#  date_gte        [2017, 2016-11-1]   # greater then equal
#  date_lte        [2018, 2016-11-1]   # less then equal
#

# =============================================
# Search view sets
# =============================================
class ElasticFilter(object):
    """
    For OpenApi documentation purposes
    return the filter fields
    """

    elastic_int_filters = [
        ('hour_gte', '0 .. 23'),
        ('hour_lte', '0 .. 23'),

        # ('minute_gte',  '0 .. 60'),
        # ('minute_lte',  '0 .. 60'),

        ('year_gte', '2016 .. 2025'),
        ('year_lte', '2016 .. 2040'),

        ('week_gte',  '0 .. 60'),
        ('week_lte',  '0 .. 60'),

        ('date_gte',  '2020, 2020-11-1'),
        ('date_lte', '2025, 2025-11-1'),

        ('month_gte', '0 .. 11'),
        ('month_lte', '0 .. 11'),
        ('day_gte',  '0 .. 6 Monday = 0'),
        ('day_lte', '0 .. 6 Monday = 0'),
        ('year', '20xx'),
        ('day', '0 .. 6'),
        ('hour', '0 .. 23'),
        ('month', '0 .. 11'),
    ]

    elastic_char_filters = [
        ('format', 'json/html'),
        ('explain', ''),
        ('stadsdeel', 'A, Z ..'),
        ('buurtcode', ''),
        ('buurtcombinatie', ''),
        ('bgt_wegdeel', ''),
        ('qualcode', """
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
        """),
        ('sperscode', """
            PermittedPRDB
            Skipped
            UnPermitted
            NotFound
            Exception
            Suspect
            PermittedHH
        """),
        ('parkeervak_soort', """
            MULDER FISCAAL
        """),
    ]

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

        for filtername, desc in self.elastic_int_filters:
            fields.append(
                coreapi.Field(
                    name=filtername,
                    required=False,
                    location='query',
                    schema=coreschema.Integer(
                        title=force_text(filtername),
                        description=force_text(desc)
                    )
                )

            )

        for filtername, desc in self.elastic_char_filters:
            fields.append(
                coreapi.Field(
                    name=filtername,
                    required=False,
                    location='query',
                    schema=coreschema.String(
                        title=force_text(filtername),
                        description=force_text(desc)
                    )
                )

            )

        return fields


class WegdelenAggregationViewSet(viewsets.ViewSet):
    """
    Given bounding box  `bbox` return aggregations
    of wegdelen / vakken derived from scandata with a
    'occupancy' values.

    - avg_occupancy
    - std_occupancy
    - min_occupancy
    - max_occupancy

    Occupancy value is determined by how many different
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
        day             [0 ..  6]
        day_gte         [0 ..  6]
        day_lte         [0 ..  6]
        month           [0 .. 11]
        month_gte       [0 .. 11]
        month_lte       [0 .. 11]
        wegdelen_size   [1 .. 190]           # amount of wegdelen to ask

        You can use date-math on date fields:
        https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math


        stadsdeel       [A ..]
        buurtcode       [A04a ..]
        buurtcombinatie [A04 ..]
        year            [2015.. 2024]
        year_gte        [2015.. 2024]
        year_lte        [2015.. 2024]
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
                    avg_occupancy: xx.xxx
                    std_occupancy: xx
                    min_occupancy: xx%
                    max_occupancy: xx%
                    wegdeelDataX: ..
                    wegdeelDataFoo: ..
                }
            }
        }

    """

    filter_backends = [ElasticFilter]

    indices = ['scans*']

    def get_queryset(self):
        """
        Not an database view..
        """
        pass

    def collect_elastic_data(
            self, bbox_values, must, wegdelen_size) -> (list, dict):
        """
        Do elastic query per index
        """

        wegdelen = {}
        responses = []

        for index in self.indices:

            log.debug(f'elk asking {index}')
            log.debug(f'Wegdelen Count {len(wegdelen)}')

            #
            elk_response, err = self.do_wegdelen_search(
                bbox_values, must,
                index=index,
                wegdelen_size=wegdelen_size)

            if settings.DEBUG:
                # Print elk response to console
                # print(json.dumps(elk_response, indent=4))
                # return Response(elk_response)
                pass

            if err:
                log.error(err)
                continue
                # return Response([err], status=500)

            # collect all wegdelen id's in elastic response
            err = collect_wegdelen(wegdelen, elk_response)

            if err:
                log.error('%s %s', index, err)
                continue

            responses.append(elk_response)

        return responses, wegdelen

    def list(self, request):
        """
        List dates with wegdeelen and distinct vakken count
        combined with meta road information
        """

        self.indices = ['scans-*']
        must = []

        err = None

        bbox_values, err = bbox.determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox_values}"], status=400)

        # clean client input
        cleaned_data, err = queries.clean_parameter_data(request.query_params)

        if err:
            return Response([f"invalid parameter {err}"], status=400)

        # adjues query parameters to available data!
        err, cleaned_data, indexes = determine_relevant_indices(cleaned_data)

        if err:
            return Response([f"Data not present. sorry {err}"], status=404)

        if indexes:
            log.debug(indexes)
            self.indices = indexes

        # get filter / must queries parts for elasti
        must = queries.build_must_queries(cleaned_data)

        # get aggregations from elastic
        wegdelen_size = cleaned_data.get('wegdelen_size', 450)

        # request data for each relevant index/day
        elk_responses, wegdelen = self.collect_elastic_data(
            bbox_values, must, wegdelen_size)

        # find and collect wegdelen meta data from DB.
        load_db_wegdelen(bbox_values, wegdelen)

        # now we have elastic data and database date to
        # calculate bezetting
        # for elk_response in responses:
        wegdelen_data = build_wegdelen_data(elk_responses, wegdelen)

        wegdelen_data = calculate_occupancy(
            wegdelen_data, request.query_params)

        return Response({
            'selection': cleaned_data,
            'wegdelen': wegdelen_data
        })

    def do_wegdelen_search(
            self, bbox_values, must=(),
            index="scans-*", wegdelen_size=90):
        """
        Given bbox find

        - distinct wegdelen seen
        - distinct vakken seen for each wegdeel with counts
        """

        elk_q = queries.build_wegdeel_query(bbox_values, must, wegdelen_size)

        build_q = json.loads(elk_q)
        log.debug(json.dumps(build_q, indent=4))

        try:
            result = ELK_CLIENT.search(
                index=index, size=0, body=elk_q)
        except Exception as exeption:   # pylint: disable=broad-except
            log.debug(exeption)
            build_q = json.loads(elk_q)
            log.debug(json.dumps(build_q, indent=4))
            return [], 'elasticsearch query failed'

        return result, None


def load_db_wegdelen(bbox_values, wegdelen):
    """
    Given aggregation counts, determine "bezetting"
    """
    lat1, lon1, lat2, lon2 = bbox_values

    poly_bbox = Polygon.from_bbox((lon1, lat1, lon2, lat2))

    wd_qs = WegDeel.objects.all().filter(
        Q(**{"geometrie__bboverlaps": poly_bbox}))

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

        bbox_values, err = bbox.determine_bbox(request)

        if err:
            return Response([f"bbox invalid {err}:{bbox_values}"], status=400)

        elk_response = self.get_aggregations(bbox_values)

        # count in involved scans
        count = elk_response.hits.total

        pv_elk = []
        parkeervakken = []
        if count:
            pv_elk = elk_response.aggregations['parkeervakken']
            parkeervakken = [(i['key'], i['doc_count']) for i in pv_elk]

        result = {
            'scancount': count,
            'vakken': parkeervakken,
        }

        return Response(result)

    def get_aggregations(self, bbox_values):
        """
        Given bbox find

        max-boundaties bounding-box. (groot Amsterdam)

                  4.58565,  52.03560,  5.31360, 52.48769,
        bbox      bottom,       left,      top,    right


        - distinct wegdelen seen
        """

        elk_q = queries.aggregation_query(bbox_values)

        search = elk_q.to_elasticsearch_object(ELK_CLIENT)

        search = self.add_agg_to_search(search)

        if settings.DEBUG:
            log.debug(json.dumps(search.to_dict(), indent=4))

        result = search.execute()

        return result

    def add_agg_to_search(self, search_object):
        """
        Find x most scanned spots
        """

        parkeervak_agg = A(
            'terms', field='parkeervak_id.keyword', size=2000)

        search_object.aggs.bucket('parkeervakken', parkeervak_agg)

        return search_object
