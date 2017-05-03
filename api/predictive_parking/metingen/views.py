import logging
import json

from rest_framework.response import Response

from rest_framework import viewsets  # , metadata

from elasticsearch import Elasticsearch

from elasticsearch_dsl import A

# from elasticsearch.exceptions import TransportError
# from elasticsearch_dsl import Search

from django.conf import settings

from datapunt import rest

from metingen import serializers

from metingen import models

from metingen import queries

log = logging.getLogger(__name__)


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


class AggregationViewSet(viewsets.ViewSet):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Amsterdam
        self.bbox = [
            52.03560, 4.58565,
            52.48769, 5.31360]

        self.elk_client = Elasticsearch(
            settings.ELASTIC_SEARCH_HOSTS,
            raise_on_error=True
        )

    def list(self, request):

        err = None

        if 'bbox' in request.query_params:
            bbox = request.query_params['bbox']
            bbox, err = valid_bbox(bbox)
        else:
            bbox = self.bbox

        if err:
            return Response([f"bbox invalid {err}:{bbox}"])

        lat1, lon1, lat2, lon2 = bbox

        # find wegdelen from DB.
        wegdelen = self.get_wegdelen(bbox)

        # get aggregations from elastic
        elk_response = self.get_aggregations(bbox)

        # count in involved scans
        count = elk_response.hits.total

        for agg in elk_response.aggregations:
            for item in agg['buckets'][:10]:
                print(item['key'], item['doc_count'])

        wd = elk_response.aggregations['wegdelen']
        pv = elk_response.aggregations['parkeervaken']

        wegdelen = [{
            "id": i['key'],
            "scan_count": i['doc_count']} for i in wd]

        parkeervakken = [(i['key'], i['doc_count']) for i in pv]

        # merge wegdelen information from db
        self.combine(elk_response, wegdelen)

        return Response({
            'bbox': [lat1, lon1, lat2, lon2],
            'wegdelen': wegdelen,
            'parkeervak': parkeervakken,
            'scancount': count,
            'scans': [h.to_dict() for h in elk_response.hits[:10]]
        })

    def get_aggregations(self, bbox):
        """
        Given bbox find

        - distinct wegdelen seen

        - distinct vakken seen, with counts

        """

        elk_q = queries.aggregation_query(bbox)

        search = elk_q.to_elasticsearch_object(self.elk_client)

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
            'terms', field='bgt_wegdeel.keyword', size=1000)

        # wegdeel

        parkeervak_agg = A(
            'terms', field='parkeervak_id.keyword', size=2000)

        search_object.aggs.bucket('wegdelen', wegdeel_agg)

        search_object.aggs.bucket('parkeervaken', parkeervak_agg)

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

    def combine(self, elk_aggregation, wegdelen):
        """
        Given aggregation counts, determine "bezetting"
        """
        assert elk_aggregation, wegdelen

        return []
