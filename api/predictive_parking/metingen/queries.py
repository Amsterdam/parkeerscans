"""
Elasticseach queries
"""
import json
from datetime import datetime, timedelta

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
    'monday   ',
    'tuesday  ',
    'wednesday',
    'thursday ',
    'friday   ',
    'saturday ',
    'sunday   ',
]

MONTHS = [
    'january  ',
    'february ',
    'march    ',
    'april    ',
    'may      ',
    'june     ',
    'july     ',
    'august   ',
    'september',
    'october  ',
    'november ',
    'december ',
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


POSSIBLE_INT_PARAMS = [
    ('hour', range(0, 24)),
    ('hour_gte', range(0, 24)),
    ('hour_lte', range(0, 24)),
    # ('minute', range(0, 60)),
    ('minute_gte', range(0, 60)),
    ('minute_lte', range(0, 60)),

    ('day', range(0, 7)),
    ('month', range(0, 12)),
    ('year', range(2015, 2025)),

    ('wegdelen_size', range(1, 60)),
]


def hour_previous():
    """
    current hour - 1
    """
    now = datetime.now()
    return (now - timedelta(hours=1)).hour


def hour_next():
    """
    current hour + 1
    """
    now = datetime.now()
    return (now + timedelta(hours=2)).hour


# Elastic date notations.
DATE_RANGE_FIELDS = [
    ('date_gte', 2017),
    ('date_lte', 2019),

    ('hour_gte', hour_previous()),
    ('hour_lte', hour_next()),
    ('day', datetime.now().weekday),
]


RANGE_FIELDS = [
    ('hour_1', 'hour_2'),
    ('minute_1', 'minute_2'),
]


def parse_int_parameters(req_params, clean_values):
    """
    Validate possible integer selections
    """

    for field_name, possiblerange in POSSIBLE_INT_PARAMS:

        value, err = parse_int_field(field_name, req_params, possiblerange)

        if err:
            return None, err
        if value:
            clean_values[field_name] = value

    return clean_values, None


def set_date_fields(req_params, clean_values):
    """
    Parse daterange or set default values
    """

    for field_name, default in DATE_RANGE_FIELDS:

        if callable(default):
            clean_values[field_name] = default()
        else:
            clean_values[field_name] = default

        if field_name in req_params:
            # can't really clean this elastic
            # date field
            clean_values[field_name] = req_params[field_name]

    return clean_values


def selection_fields(req_params, clean_values):
    """
    Clean filter options
    """
    err = None

    for field_name, options in TERM_FIELDS.items():
        if field_name in req_params:
            filter_value = req_params[field_name]
            if options and filter_value not in options:
                err = f'{field_name}{filter_value} not in {options}'
            else:
                clean_values[field_name] = filter_value

    return clean_values, err


def parse_parameter_input(request):
    """
    Validate client input
    """
    err = None

    req_params = request.query_params

    clean_values = {}

    clean_values, err = parse_int_parameters(req_params, clean_values)

    if err:
        return None, err

    err = validate_range_fields(clean_values)

    # Parse date fields and set default
    clean_values = set_date_fields(req_params, clean_values)

    clean_values, err = selection_fields(req_params, clean_values)

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

    if not value.isdigit():
        field = "%s.keyword" % field
    else:
        value = int(value)

    q = {
        "term": {
            field: value
        }
    }

    return q

# we provide optional list of options
# for better error reporting

TERM_FIELDS = {
    'hour': None,
    'stadsdeel': None,
    'buurtcode': None,
    'buurtcombinatie': None,
    'bgt_wegdeel': None,
    'year': None,
    'qualcode': None,
    'sperscode': None,
}


def make_terms_queries(cleaned_data):
    """
    Given cleaned data build some elastic term queries
    """
    term_q = []

    for field in TERM_FIELDS:
        if field in cleaned_data:
            f_q = build_term_query(field, cleaned_data[field])
            term_q.append(f_q)

    if 'day' in cleaned_data:
        if isinstance(cleaned_data['day'], int):
            day = DAYS[int(cleaned_data['day'])]
            f_q = build_term_query('day', day)
            term_q.append(f_q)
        # ignore day filter

    if 'month' in cleaned_data:
        month = MONTHS[int(cleaned_data['month'])]
        f_q = build_term_query('month', month)
        term_q.append(f_q)

    return term_q


def make_range_q(field, gte_field, lte_field, cleaned_data):
    """
    Build a range query for fieldx
    """
    if field in cleaned_data:
        if gte_field in cleaned_data:
            del cleaned_data[gte_field]
        if lte_field in cleaned_data:
            del cleaned_data[lte_field]

        # range makes no sense..when haveing specific value
        return

    low = cleaned_data.get(gte_field)
    high = cleaned_data.get(lte_field)

    if low is None or high is None:
        # do not build range query
        return

    range_q = {
        "range": {
            f"{field}": {
                "gte": low,
                "lte": high,
            }
        }
    }

    return range_q


def clean_parameter_data(request):
    """
    clean client input
    """

    err = None

    clean_values, err = parse_parameter_input(request)

    if err:
        return [], err

    return clean_values, err


def build_must_queries(cleaned_data):
    """
    Given request parameters

    build query parts
    """

    must = []

    terms_q = make_terms_queries(cleaned_data)
    m_range_q = make_range_q(
        'minute', 'minute_gte', 'minute_lte', cleaned_data)
    h_range_q = make_range_q(
        'hour', 'hour_gte', 'hour_lte', cleaned_data)
    d_range_q = make_range_q(
        'day', 'day_gte', 'day_lte', cleaned_data)

    date_range_q = make_range_q(
        '@timestamp', 'date_gte', 'date_lte', cleaned_data)

    must.extend(terms_q)

    if h_range_q:
        must.append(h_range_q)
    if m_range_q:
        must.append(m_range_q)
    if date_range_q:
        must.append(date_range_q)

    if d_range_q:
        must.append(d_range_q)

    return must


def build_wegdeel_query(bbox, must, wegdelen_size=20):
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
                            "size": wegdelen_size
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
