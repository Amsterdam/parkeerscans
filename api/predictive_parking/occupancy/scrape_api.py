"""
Load occupancy from our own elastic API
in the database for easy to consume datasets
"""
import logging

from datetime import datetime
from datetime import timedelta

from collections import namedtuple

import time
import psycopg2
import requests

from django.db.models import F, Count

from django.conf import settings
from django.db import connection
from django.test import Client

from occupancy.models import RoadOccupancy
from occupancy.models import Selection


log = logging.getLogger(__name__)   # noqa


API_ROOT = 'https://acc.api.data.amsterdam.nl'
# API_ROOT = 'http://127.0.0.1:8000'
API_PATH = '/predictiveparking/metingen/aggregations/wegdelen/'

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
    (0, 23),   # dag
]


MONTH_RANGE = [
    # (0, 3),
    # (4, 6),
    (3, 7),
    # (10, 12),
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
    'bucket', ['y1', 'y2', 'm1', 'm2', 'd1', 'd2', 'h1', 'h2', 'qcode'])


def make_year_month_range():
    """
    now - 3 months
    """
    delta = timedelta(days=30)
    today = datetime.today()

    before = today - delta

    year1 = before.year
    year2 = today.year

    month1 = before.month - 1   # we start at 0
    month2 = today.month - 1   # we start at 0

    return year1, year2, month1, month2


def occupancy_buckets():
    """
    Determine the occupancy buckets
    we need
    """
    buckets = []

    y1, y2, m1, m2 = make_year_month_range()

    for d1, d2 in DAY_RANGE:
        for h1, h2 in HOUR_RANGE:
            # Bezoekers of niet.
            for q in [None, 'BETAALDP']:
                b = Bucket(y1, y2, m1, m2, d1, d2, h1, h2, q)
                buckets.append(b)

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

    if len(manual_selection) == 8:
        # qualcode is None
        manual_selection.append('')

    assert len(manual_selection) == 9
    assert min(manual_selection[:8]) >= 0
    b = Bucket(*manual_selection)
    # add the new selection
    create_selections([b])


def validate_selection(bucket):
    b = bucket
    # lets do some validation..
    assert b.y1 in range(2016, 2025)
    assert b.y2 in range(2016, 2025)
    assert b.m1 in range(0, 12)
    assert b.m2 in range(0, 12)
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
            # parking sport dissapeared?
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

    todo_selections = Selection.objects.filter(status__isnull=True).count()
    done_selections = Selection.objects.filter(status__isnull=False).count()

    log.info(f'Selections: TODO: {todo_selections} READY: {done_selections}')


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
        'month_gte': s.month1,
        'month_lte': s.month2,
        'day_gte': s.day1,
        'day_lte': s.day2,
        'hour_gte': s.hour1,
        'hour_lte': s.hour2,
        'wegdelen_size': 8000,
    }

    if s.qualcode:
        payload['qualcode'] = s.qualcode

    if settings.TESTING:
        response = TEST_CLIENT.get(API_PATH, payload)
        return response.data
    else:
        response = requests.get(API_URL, payload)

    if response.status_code != 200:
        log.error('%s %s', response.status_code, payload)
        selection.status = None
        selection.save()
        log.debug('Waiting a bit..')
        time.sleep(30)
        return
        # raise ValueError

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

        store_selection_status(selection)

    #work_count = work_selections.count()

    #if work_count:
    #    log.debug('not done yet.. lets retry')
    #    fill_occupancy_roadparts(count=count)


def execute_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def create_selection_tables():
    """
    Create tables of selections usable for mapserver / qgis

    We make tables for ease of dumping / restoring tables
    """

    work_done = Selection.objects.filter(status=1)

    for selection in work_done:
        view_name = selection.view_name()

        log.info('Created view %s', view_name)
        # create view for each selection with
        # geometry data.

        sql = f"""
DROP TABLE IF EXISTS sv{str(view_name)};
SELECT * INTO sv{str(view_name)} FROM (
SELECT
    row_number() OVER (ORDER BY wd.bgt_id) as id,
    wd.bgt_id,
    wd.vakken,
    wd.fiscale_vakken,
    occupancy,
    min_occupancy,
    max_occupancy,
    std_occupancy, unique_scans,
    b.code,
    wd.geometrie
FROM wegdelen_wegdeel wd, occupancy_roadoccupancy oc,
     occupancy_selection s, wegdelen_buurt b
WHERE wd.bgt_id = oc.bgt_id
AND ST_Contains(b.geometrie, wd.geometrie)
AND wd.vakken >= 3
AND s.id = oc.selection_id
AND s.id = {selection.id}) as tmptable
        """
        execute_sql(sql)


def dump_csv_files():
    """
    For each view create a csv file.
    """

    work_done = Selection.objects.filter(status=1)

    for selection in work_done:
        view_name = selection.view_name()

        select = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken,
            min_occupancy, max_occupancy, std_occupancy, unique_scans,
            code,
            ST_AsText(geometrie)
        FROM sv{str(view_name)}
        """

        select_no_geo = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken
            min_occupancy, max_occupancy, std_occupancy, unique_scans,
            code
        FROM sv{str(view_name)}
        """

        outputquery = f"COPY ({select}) TO STDOUT WITH CSV HEADER"
        outputquery_no_geo = f"COPY ({select_no_geo}) TO STDOUT WITH CSV HEADER"   # noqa

        file_name = f'{settings.CSV_DIR}/{str(view_name)}.csv'
        file_name_no_geo = f'{settings.CSV_DIR}/{str(view_name)}.nogeo.csv'

        with connection.cursor() as cursor:

            try:
                with open(file_name, 'w') as csvfile:
                    log.debug('saving view: %s', file_name)
                    cursor.copy_expert(outputquery, csvfile)

                with open(file_name_no_geo, 'w') as csvfile:
                    log.debug('saving view: %s', file_name_no_geo)
                    cursor.copy_expert(outputquery_no_geo, csvfile)

            except psycopg2.ProgrammingError:
                log.exception('table missing')
