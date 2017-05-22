"""
Elasticseach queries
"""
import json

from elasticsearch_dsl import Search


class ElasticQueryWrapper(object):
    """
    Wrapper object for dynamically constructing elastic search queries.
    """

    def __init__(
            self, query,
            indexes: [str] = None,
            aggs=(),
            filters=(),
            size: int = None):
        """
        :param query: an elastic search query
        :param sort_fields: an optional list of fields
            to use for server-side sorting
        :param indexes: an optional list of indexes to use

        :param size: an optional limit on size of
            the result set
        """
        self.query = query
        self.indexes = indexes
        self.size = size
        self.aggs = aggs
        self.filters = filters

    def to_elasticsearch_object(self, client) -> Search:
        assert self.indexes

        search = (
            Search()
            .using(client)
            .index(*self.indexes)
            .query(self.query)
        )

        if self.filters:
            search = search.filter(*self.filters)

        # sample size
        size = 2  # default size

        if self.size:
            size = self.size

        search = search[0:size]

        return search


def aggregation_query(bbox):
    """
    Crate aggregation query
    """
    bbox_f = build_bbox_filter(bbox)

    elk_q = ElasticQueryWrapper(
        query={'match_all': {}},
        indexes=["scans-*", ],
        filters=[bbox_f],
    )

    return elk_q


def build_bbox_filter(bbox):
    """
    build bbox part of query
    """

    bottom, left, top, right = bbox

    bbox_f = {
        "geo_bounding_box": {
            "geo": {
                "top": top,
                "left": left,
                "bottom": bottom,
                "right": right,
            }
        }
    }

    return bbox_f


DAYS = [
    'monday',
    'tuesday'
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
]


def parse_int(value, _range=()):
    """
    Check if value is int in range

    return int and error if any.
    """

    err = None
    parsed = None

    try:
        parsed = int(value)
        if _range and parsed not in _range:
            err = "range error"
    except ValueError:
        err = "invalid"

    return parsed, err


def parse_int_field(field_name, params, _range):
    """
    Parse a field from parameters
    """
    field_value = None
    err = None

    if field_name in params:
        field_value = params[field_name]
        field_value, err = parse_int(field_value, _range)

    if err:
        err = f'invalid {field_name}{field_value}'

    return field_value, err


POSSIBLE_PARAMS = [
    ('hour', range(0, 24)),
    ('hour_1', range(0, 24)),
    ('hour_2', range(0, 24)),
    # ('minute', range(0, 60)),
    ('minute_1', range(0, 60)),
    ('minute_2', range(0, 60)),
    ('day', DAYS),
]

DATE_RANGE_FIELDS = [
    ('date_gte', 2017),
    ('date_lte', 2018),
]


RANGE_FIELDS = [
    ('hour_1', 'hour_2'),
    ('minute_1', 'minute_2'),
]


def parsed_date_range(field, default, req_params):
    """
    Check date range given by client.
    """
    return

    # TODO

    # value = default

    # if field in req_params:


def parse_parameter_input(request):
    """
    Validate client input
    """

    req_params = request.query_params

    clean_values = {}

    for field_name, _range in POSSIBLE_PARAMS:

        value, err = parse_int_field(field_name, req_params, req_params)
        if err:
            return None, err
        if value:
            clean_values[field_name] = value

    for field_name, default in DATE_RANGE_FIELDS:
        clean_values[field_name] = default

    err = validate_range_fields(clean_values)

    return clean_values, err


def validate_range_fields(clean_values):

    err = None

    for low, high in RANGE_FIELDS:
        if low not in clean_values:
            continue
        if high in clean_values:
            low_value = clean_values[low]
            high_value = clean_values[high]
            if high_value < low_value:
                err = "!! hour_2 < hour_1"
        err = f'{high} missing'

    return err


def build_term_query(field, value):
    """
    Build a term query for a field
    """

    if isinstance(value, str):
        field = "%s.keyword" % field

    q = {
        "terms": dict(field=value)
    }

    return q

TERM_FIELDS = [
    'hour',
    'day',
    'stadsdeel',
    'buurtcode',
    'buurtcombinatie',
    'parkeervak_soort',
    'parkeervak_id',
    'bgt_wegdeel',
    'year',
    'month',
    'qualcode',
    'sperscode',
]


def make_terms_queries(cleaned_data):
    """
    Given cleaned data build some elastic term queries
    """
    term_q = []

    for field in ['hour', 'day']:
        if field in cleaned_data:
            f_q = build_term_query(field, cleaned_data[field])
            term_q.append(f_q)

    return term_q


def make_range(field, low_field, high_field, cleaned_data):
    """
    Build a range query for fieldx
    """
    low = cleaned_data.get(low_field)
    high = cleaned_data.get(high_field)

    if low is None or high is None:
        return

    # is checked in parameter cleanup
    assert low <= high

    range_q = {
        "range": {
            f"{field}": {
                "gte": low,
                "lte": high,
            }
        }
    }

    return range_q


def build_must_queries(request):
    """
    Given request parameters

    build query parts
    """

    must = []
    err = None

    cleaned_data, err = parse_parameter_input(request)

    if err:
        return [], err

    terms_q = make_terms_queries(cleaned_data)
    m_range_q = make_range('minute', 'minute_1', 'minute_2', cleaned_data)
    h_range_q = make_range('hour', 'hour_1', 'hour_2', cleaned_data)

    date_range_q = make_range(
        '@timestamp', 'date_gte', 'date_lte', cleaned_data)

    must.extend(terms_q)

    if h_range_q:
        must.append(h_range_q)
    if m_range_q:
        must.append(m_range_q)
    if date_range_q:
        must.append(date_range_q)

    return must, err


def build_wegdeel_query(bbox, must):
    """
    Build aggregation determine distinct vakken for
    each wegdeel per day.
    """

    bbox_f = build_bbox_filter(bbox)

    query_part = {
        "bool": {
            "must": [*must],
            "filter": bbox_f,
        },
    }

    size = 10

    wegdeel_agg = {
        "aggs": {
            "scan_by_date": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1d",
                    "format": "yyyy-MM-dd",
                    "keyed": True
                },
                "aggs": {

                    "wegdeel": {
                        "terms": {
                            "field": "bgt_wegdeel.keyword",
                            "size": size
                        },
                        "aggs": {
                            "hour": {
                                "terms": {
                                    "field": "hour",
                                    "size": 20,
                                },
                                "aggs": {
                                    "vakken": {
                                        "cardinality": {
                                            "field": "parkeervak_id.keyword"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    wegdeel_agg["query"] = query_part

    return json.dumps(wegdeel_agg)


def build_wegdeel_weekday_query(bbix, must):
    """
    """

