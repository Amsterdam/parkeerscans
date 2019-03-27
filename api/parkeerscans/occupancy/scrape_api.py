"""
Load occupancy from our own elastic API
in the database for easy to consume datasets
"""
import os
import sys
import logging

from datetime import datetime
from datetime import timedelta

from collections import namedtuple

import time
import requests

from django.db.models import F, Count

from django.conf import settings
from django.test import Client

from occupancy.models import RoadOccupancy
from occupancy.models import Selection


log = logging.getLogger(__name__)   # noqa

# API_ROOT = 'https://acc.api.data.amsterdam.nl'
API_ROOT = 'http://127.0.0.1:8000'

if os.getenv('ENVIRONMENT', '') == 'production':
    API_ROOT = 'https://api.data.amsterdam.nl'

# API_ROOT = 'http://127.0.0.1:8000'
API_PATH = '/parkeerscans/metingen/aggregations/wegdelen/'

API_URL = f'{API_ROOT}{API_PATH}'

TEST_CLIENT = None

if settings.TESTING:
    TEST_CLIENT = Client()


HOUR_RANGE = [
    (9, 12),   # ochtend
    (13, 16),  # middag
    (17, 19),  # spits
    (20, 23),  # avond
    (0, 4),    # nacht
    # (0, 23),   # dag
]


DAY_RANGE = [
    # (0, 6),  # hele week too heavy!
    (0, 4),  # werkdag
    (5, 6),  # weekend

    (0, 0),  # maandag
    (1, 1),  # dinsdag
    (2, 2),  # woensdag
    (3, 3),  # donderdag
    (4, 4),  # vrijdag
    (5, 5),  # zaterdag
    (6, 6),  # zondag
]


year_range = [
    (2017, 2017),
]


Bucket = namedtuple(
    'bucket', [
        'y1', 'y2',
        'm1', 'm2',
        'd1', 'd2',
        'h1', 'h2',
        'w1', 'w2',
        'qcode'
    ])


def make_time_range():
    """
    now - 3 months
    """
    delta = timedelta(days=90)
    today = datetime.today()

    before = today - delta

    year1 = before.year
    year2 = today.year

    month1 = before.month - 1   # we start at 0
    month2 = today.month - 1    # we start at 0

    week1 = before.isocalendar()[1]
    week2 = today.isocalendar()[1]

    return year1, year2, month1, month2, week1, week2


def time_range(w1, w2, options):

    if w1 < w2:
        return options[w1:w2]

    return options[w1:] + options[:w2]


def make_week_buckets(
        buckets: list,
        y1: int, y2: int,
        w1: int, w2: int,
        d1: int, d2: int,
        h1: int, h2: int,
        q: str):
    """
    Make selection bucket objects for weeks
    """
    for w in time_range(w1, w2, list(range(1, 53))):

        if y1 != y2:
            if w >= w1:
                # year1
                b = Bucket(y1, y1, None, None, d1, d2, h1, h2, w, w, q)
                buckets.append(b)
            else:
                # year2
                b = Bucket(y2, y2, None, None, d1, d2, h1, h2, w, w, q)
                buckets.append(b)
        else:
            # same year
            b = Bucket(y1, y1, None, None, d1, d2, h1, h2, w, w, q)
            buckets.append(b)


def make_month_buckets(
        buckets: list,
        y1: int, y2: int,
        m1: int, m2: int,
        d1: int, d2: int,
        h1: int, h2: int,
        q: str):
    """
    Make selection bucket objects for months
    """

    for m in time_range(m1, m2, list(range(0, 12))):
        if y1 != y2:
            if m >= m1:
                # year1
                b = Bucket(y1, y1, m, m, d1, d2, h1, h2, None, None, q)
                buckets.append(b)
            else:
                # year2
                b = Bucket(y2, y2, m, m, d1, d2, h1, h2, None, None, q)
                buckets.append(b)
        else:
            # same year
            b = Bucket(y1, y2, m, m, d1, d2, h1, h2, None, None, q)
            buckets.append(b)


def occupancy_buckets():
    """
    Determine the occupancy buckets we need
    """
    buckets = []

    y1, y2, m1, m2, w1, w2 = make_time_range()

    for d1, d2 in DAY_RANGE:
        for h1, h2 in HOUR_RANGE:
            # Bezoekers of niet.
            for q in [None, 'BETAALDP']:
                # make_month_buckets(buckets, y1, y2, m1, m2, d1, d2, h1, h2, q)
                make_week_buckets(buckets, y1, y2, w1, w2, d1, d2, h1, h2, q)

    return buckets


def create_selections(buckets):
    """
    For selection buckets
    """

    for b in buckets:
        assert validate_selection(b)

        Selection.objects.get_or_create(
            day1=b.d1,
            day2=b.d2,
            hour1=b.h1,
            hour2=b.h2,
            month1=b.m1,
            month2=b.m2,
            week1=b.w1,
            week2=b.w2,
            year1=b.y1,
            year2=b.y2,
            qualcode=b.qcode,
        )


def create_single_selection(longstring):
    """
    Create a manual selection

    validate input..
    """
    manual_selection = longstring.split(':')

    manual_selection = list(map(int, manual_selection))

    if len(manual_selection) == 10:
        # qualcode is None
        manual_selection.append('')

    assert len(manual_selection) == 11
    assert min(manual_selection[:10]) >= 0

    b = Bucket(*manual_selection)
    # add the new selection
    create_selections([b])


def validate_selection(bucket):
    b = bucket
    # lets do some validation..
    assert b.y1 in range(2016, 2035)
    assert b.y2 in range(2016, 2035)

    if b.m1:
        assert b.m1 in range(0, 12)
    if b.m2:
        assert b.m2 in range(0, 12)

    if b.w1:
        assert b.w1 in range(1, 53)
    if b.w2:
        assert b.w2 in range(1, 53)

    assert (b.m1 is not None or b.w1 is not None)

    assert b.d1 in range(0, 7)
    assert b.d2 in range(0, 7)
    assert b.h1 in range(0, 24)
    assert b.h2 in range(0, 24)
    assert b.y1 <= b.y2
    assert b.d1 <= b.d2
    assert b.h1 <= b.h2

    return True


# make sure selections and weg_id are unique
# selection_road_mapping = {}


def store_occupancy_data(json: dict, selection: dict):

    if not json:
        return 0

    for wd_id, wd_data in json['wegdelen'].items():

        avg_occupancy = wd_data.get('avg_occupancy')
        min_occupancy = wd_data.get('min_occupancy')
        max_occupancy = wd_data.get('max_occupancy')
        std_occupancy = wd_data.get('std_occupancy')

        if not avg_occupancy:
            # no occupancy ?
            # parking spot dissapeared?
            continue

        r, created = RoadOccupancy.objects.get_or_create(
            bgt_id=wd_id,
            selection=selection,
        )

        # float fields elastic - postgres are different
        # so get_or_create will not work
        if created is False:
            continue
        else:
            r.occupancy = avg_occupancy
            r.min_occupancy = min_occupancy
            r.max_occupancy = max_occupancy
            r.std_occupancy = std_occupancy
            r.unique_scans = wd_data.get('unique_scans')
            r.save()

    wd_count = RoadOccupancy.objects.filter(selection__id=selection.id).count()
    # check how many roadpards are now available for selection
    return wd_count


def create_selection_buckets():
    buckets = occupancy_buckets()
    create_selections(buckets)

    todo_selections = Selection.objects.filter(status__isnull=True)
    done_selections = Selection.objects.filter(status__isnull=False)

    for selection in todo_selections:
        log.debug(repr(selection))

    log.info(
        f"""Selections:
            TODO:  {todo_selections.count()}
            READY: {done_selections.count()}
        """)


def get_work_to_do():
    """
    Determine which selections need to be done
    """

    work_selections = Selection.objects.filter(status__isnull=True)

    log.debug('Selections to load: %d', work_selections.count())

    # select a part
    part = settings.SCRAPE['IMPORT_PART']
    if part:
        work_selections = (
            work_selections
            .annotate(idmod=F('id') % 4)
            .filter(idmod=part-1))
        log.info(
            'Doing chunck %d of 4 left: %d',
            part, work_selections.count())

    return work_selections


def do_request(selection: dict) -> dict:
    """
    Build a single request to PP api.
    """
    s = selection

    payload = {
        'year_gte': s.year1,
        'year_lte': s.year2,
        'day_gte': s.day1,
        'day_lte': s.day2,
        'hour_gte': s.hour1,
        'hour_lte': s.hour2,
        'wegdelen_size': 8000,
    }

    if s.month1 is not None:
        payload.update({
            'month_gte': s.month1,
            'month_lte': s.month2,
        })
    else:
        payload.update({
            'week_gte': s.week1,
            'week_lte': s.week2,
        })

    if s.qualcode:
        payload['qualcode'] = s.qualcode

    if settings.TESTING:
        response = TEST_CLIENT.get(API_PATH, payload)
        return response.data
    else:
        response = requests.get(API_URL, payload)

    log.debug(response.url)

    if response.status_code == 500:
        # server error.
        log.error('%s %s', response.status_code, payload)
        log.error(response.url)
        selection.status = None
        selection.save()
        raise ValueError('API Server gives 500')

    elif response.status_code == 404:
        # nothing found.
        selection.delete()
        log.debug('No data available')
        return

    elif response.status_code == 504:
        # timeout.
        log.error('%s %s', response.status_code, payload)
        log.error(response.url)
        selection.status = None
        selection.save()
        log.debug('Waiting a bit..')
        time.sleep(30)
        return

    elif response.status_code != 200:
        # server error.
        log.error('%s %s', response.status_code, payload)
        log.error(response.url)
        selection.status = None
        selection.save()
        raise ValueError(f'API Server gives {response.status}')

    return response.json()


def store_selection_status(selection):
    """
    Given selection
    """
    wd_count = (
        RoadOccupancy.objects.select_related()
        .filter(selection_id=selection.id)
        .values_list('selection_id')
        .annotate(wdcount=Count('selection_id'))
    )

    # mark this selection as done.
    selection.status = 1
    selection.save()

    if len(wd_count):
        log.info(f'Roadparts {wd_count[0][1]} for {selection}')


def validate_scraping():
    """Make sure we have occupancy data.
    """
    summary = (
        RoadOccupancy.objects.values('selection_id')
        .annotate(wdcount=Count('selection_id'))
        .order_by('-wdcount')[:20]
    )

    for item in summary:
        s_id = item['selection_id']
        count = item['wdcount']
        s = Selection.objects.get(pk=s_id)
        log.info("%s wegdelen: %s", repr(s), count)

    selections = (
        RoadOccupancy.objects.values('selection_id')
        .annotate(wdcount=Count('selection_id'))
        .order_by('-wdcount'))

    if not selections:
        raise ValueError('No occupancy data present.')

    count = selections.first()['wdcount']

    if count == 0:
        raise ValueError('No occupancy data present..')

    log.info('seems ok')


def fill_occupancy_roadparts(count=0):
    """
    Fill occupancy table with occupancy
    cijfers
    """
    if count > 10:
        # stop retrying
        return

    count += 1

    work_selections = get_work_to_do()

    work_count = work_selections.count()

    for i, selection in enumerate(work_selections):
        _s = selection

        log.info(f'Working on {_s.id} {_s.view_name()}')

        response_json = do_request(selection)

        if not response_json:
            continue

        wd_count = store_occupancy_data(response_json, selection)

        log.debug(
            '%d of %d: %4s wegdelen: %d',
            i, work_count, selection._name(),
            wd_count
        )
        if wd_count < 10:
            log.info(f'No results for {selection}. remove')
            selection.delete()

        store_selection_status(selection)
