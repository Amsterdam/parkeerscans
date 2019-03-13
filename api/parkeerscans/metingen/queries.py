"""
Elasticseach queries
"""
import re
import json
import logging

from datetime import datetime, timedelta

from elasticsearch_dsl import Search

log = logging.getLogger(__name__)


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

    # increase the bbox to avoid low values for
    # because parts of the road are off screen

    bbox_f = {
        "geo_bounding_box": {
            "geo": {
                "top": top + 0.0004,
                "left": left - 0.004,
                "bottom": bottom - 0.004,
                "right": right + 0.004,
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
        err = f"{parsed} invalid"

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
        err = f'invalid {field_name} - {field_value} {err}'

    return field_value, err


POSSIBLE_INT_PARAMS = [
    ('hour', range(0, 24)),
    ('hour_gte', range(0, 24)),
    ('hour_lte', range(0, 24)),

    # Disable minute by minute view
    # ('minute', range(0, 60)),
    # ('minute_gte', range(0, 60)),
    # ('minute_lte', range(0, 60)),

    ('week', range(1, 53)),
    ('week_gte', range(1, 53)),
    ('week_lte', range(1, 53)),

    ('day', range(0, 7)),
    ('day_gte', range(0, 7)),
    ('day_lte', range(0, 7)),

    ('month', range(0, 12)),
    ('month_gte', range(0, 12)),
    ('month_lte', range(0, 12)),

    ('year', range(2015, 2035)),
    ('year_gte', range(2015, 2035)),
    ('year_lte', range(2015, 2035)),

    ('wegdelen_size', range(1, 9000)),
]

# we provide optional list of options
# for better error reporting

TERM_FIELDS = {
    'stadsdeel': ['A', 'K', 'E', 'N', 'M', 'F', 'T'],
    'buurtcode': None,
    'buurtcombinatie': None,
    'bgt_wegdeel': None,
    'year': None,
    'day': None,
    'week': None,
    'hour': None,
    'month': None,
    # 'minute': None,
    'qualcode': None,
    'sperscode': None,
    'parkeervak_soort': None,
}


POSSIBLE_PARAMS = [v[0] for v in POSSIBLE_INT_PARAMS]

POSSIBLE_PARAMS.extend([
    'date_lte',  # elstic date math
    'date_gte',  # elstic date math
    'format',    # json / api
    'explain',   # give bigger respnse explaining calculation
    'bbox',      # give map bbox
])

POSSIBLE_PARAMS.extend(TERM_FIELDS.keys())


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
    ('year_gte', 2017),
    ('year_lte', 2025),

    ('hour_gte', hour_previous()),
    ('hour_lte', hour_next()),

    ('day', datetime.now().weekday),
    # ('day_gte', datetime.now().weekday),
    # ('day_lte', datetime.now().weekday),
]


RANGE_FIELDS = [
    ('hour_gte', 'hour_lte'),
    ('minute_gte', 'minute_lte'),
    ('year_gte', 'year_lte'),
    ('month_gte', 'month_lte'),
    ('day_gte', 'day_lte'),
    ('week_gte', 'week_lte'),
]


def check_all_paramaters(req_params, clean_values):
    """
    Check if we recieve valid known paramaters
    """
    for field in req_params:
        if field not in POSSIBLE_PARAMS:
            return f'invalid parameter {field}'

    # clean up date_* fields these are
    # the only fields that are not forced
    # into a type since it can contain elasticsearch
    # date-math. We do some cleaning here.
    for field in ['date_gte', 'date_lte']:
        if field not in req_params:
            continue
        date_data = req_params[field]
        cleaned_date = re.sub(r'[\\/*:\{\}"\)\(|]', "", date_data)
        clean_values[field] = cleaned_date


def parse_int_parameters(req_params, clean_values):
    """
    Validate possible integer selections
    """

    for field_name, possiblerange in POSSIBLE_INT_PARAMS:
        value, err = parse_int_field(field_name, req_params, possiblerange)

        if err:
            return err

        if value is not None:
            clean_values[field_name] = value

    return None


def set_date_fields(clean_values):
    """
    set default values to specific small date range
    so the default behaviour will not overload the
    elasticsearch queries
    """

    for field_name, default in DATE_RANGE_FIELDS:

        if field_name in clean_values:
            # user already set a value for this field
            continue

        if callable(default):
            clean_values[field_name] = default()
        else:
            clean_values[field_name] = default


def selection_fields(req_params, clean_values):
    """
    Clean filter options
    """
    err = None

    for field_name, options in TERM_FIELDS.items():
        if field_name in req_params:
            if field_name in clean_values:
                filter_value = clean_values[field_name]
            else:
                filter_value = req_params[field_name]
            if options and filter_value not in options:
                err = f'{field_name}{filter_value} not in {options}'
            else:
                clean_values[field_name] = filter_value

    return err


def parse_parameter_input(query_params):
    """
    Validate client input
    """
    err = None

    clean_values = {}

    err = check_all_paramaters(query_params, clean_values)
    if err:
        return None, err

    err = parse_int_parameters(query_params, clean_values)

    if err:
        return None, err

    # set defaults date filtering if not set by user
    set_date_fields(clean_values)
    # set soort is fiscaal
    clean_values['parkeervak_soort'] = 'FISCAAL'

    err = selection_fields(query_params, clean_values)

    if err:
        return None, err

    return clean_values, None


def build_term_query(field, value):
    """
    Build a term query for a field
    """

    if not isinstance(value, int) and not value.isdigit():
        field = "%s.keyword" % field
    else:
        value = int(value)

    q = {
        "term": {
            field: value
        }
    }

    return q


def make_terms_queries(cleaned_data):
    """
    Given cleaned data build some elastic term queries

    day, month,
    """
    term_q = []

    for m_field in ['month', 'month_gte', 'month_lte']:
        if m_field in cleaned_data:
            cleaned_data[m_field] = MONTHS[
                int(cleaned_data[m_field])]

    if 'day' in cleaned_data:
        cleaned_data['day'] = DAYS[int(cleaned_data['day'])]

    for field in TERM_FIELDS:
        if field in cleaned_data:
            f_q = build_term_query(field, cleaned_data[field])
            term_q.append(f_q)

    return term_q


def clean_ambigious_fields(field, gte_field, lte_field, cleaned_data):
    """
    remove ambigious filters
    """

    if field in cleaned_data:
        if gte_field in cleaned_data:
            del cleaned_data[gte_field]
        if lte_field in cleaned_data:
            del cleaned_data[lte_field]


def make_range_q(field, gte_field, lte_field, cleaned_data):
    """
    Build a range query for field_X
    """
    clean_ambigious_fields(field, gte_field, lte_field, cleaned_data)

    # range makes no sense..when specific value is set
    if field in cleaned_data:
        return

    low = cleaned_data.get(gte_field)
    high = cleaned_data.get(lte_field)

    if low is None or high is None:
        # do not build range query
        return

    range_q = {
        "range": {
            f"{field}": {
                "gte": int(low),
                "lte": int(high),
            }
        }
    }

    return range_q


def find_options(low, high, size):
    """
    Given range find which index values we need

    first case
    1, 4 -> 1 2 3 4

    second case
    11, 2 -> 11, 0, 1, 2
    """

    if low < high:
        # normal case
        return list(range(int(low), int(high)+1))

    if low == high:
        return [low]

    # we go past the size
    end_options = list(range(size))[low:]
    start_options = list(range(size))[:high+1]
    return end_options + start_options


def make_field_bool_query(
        field, field_gte, field_lte,
        cleaned_data, all_options):
    """
    Days are a special case.

    conert day ints to strings.

    0 => monday
    """
    # clean_ambigious_fields(day, day_gte, day_lte, cleaned_data)
    if field_gte in cleaned_data and field_lte in cleaned_data:
        if field in cleaned_data:
            del cleaned_data[field]

    low = cleaned_data.get(field_gte)
    high = cleaned_data.get(field_lte)

    if low is None or high is None:
        # do not build range query
        return

    involved_terms = []

    should = []

    for x in find_options(low, high, len(all_options)):
        involved_terms.append(all_options[int(x)])

    for stringfield in involved_terms:
        should.append(
            {"term": {
                f"{field}.keyword": stringfield}})

    if not should:
        return

    field_bool_q = {
        "bool": {
            "should": should
        }
    }

    return field_bool_q


def clean_parameter_data(query_params):
    """
    clean client input from the evil internets
    """

    err = None

    cleaned_data, err = parse_parameter_input(query_params)

    if err:
        return {}, err

    return cleaned_data, None


def build_must_queries(cleaned_data):
    """
    Given request parameters

    build query parts
    """

    must = []

    m_range_q = make_range_q(
        'minute', 'minute_gte', 'minute_lte', cleaned_data)

    h_range_q = make_range_q(
        'hour', 'hour_gte', 'hour_lte', cleaned_data)

    year_range_q = make_range_q(
        'year', 'year_gte', 'year_lte', cleaned_data)

    month_bool_q = make_field_bool_query(
        'month', 'month_gte', 'month_lte',
        cleaned_data, MONTHS)

    day_bool_q = make_field_bool_query(
        'day', 'day_gte', 'day_lte',
        cleaned_data, DAYS)

    date_range_q = make_range_q(
        '@timestamp', 'date_gte', 'date_lte', cleaned_data)

    # make selection human readable and
    # and create term queries if needed.
    terms_q = make_terms_queries(cleaned_data)

    must.extend(terms_q)

    if h_range_q:
        must.append(h_range_q)
    if m_range_q:
        must.append(m_range_q)
    if date_range_q:
        must.append(date_range_q)
    if month_bool_q:
        must.append(month_bool_q)
    if year_range_q:
        must.append(year_range_q)

    if day_bool_q:
        must.append(day_bool_q)

    return must


def build_wegdeel_query(bbox, must, wegdelen_size=260):
    """
    Build aggregation determine distinct vakken for
    each wegdeel per day per hour.

    ~8000 wegdelen is the entire city.

    DO not ask for more then ~7 days at once.
    """

    bbox_f = build_bbox_filter(bbox)

    query_part = {
        "bool": {
            "must": [],
            "filter": [bbox_f, *must]
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
                                    "size": 24,
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
