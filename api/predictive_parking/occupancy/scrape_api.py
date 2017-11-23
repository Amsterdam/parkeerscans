"""
Load occupancy from our own elastic API
in the database for easy to consume datasets
"""
import logging
import requests
from datetime import datetime
from datetime import timedelta

from collections import namedtuple
from django.db.models import F, Count

from django.conf import settings
from django.db import connection
from django.test import Client

from wegdelen.models import WegDeel
from wegdelen.models import Buurt
from occupancy.models import RoadOccupancy
from occupancy.models import Selection


log = logging.getLogger(__name__)


API_ROOT = 'https://acc.api.data.amsterdam.nl'
API_PATH = '/predictiveparking/metingen/aggregations/wegdelen/'

API_URL = f'{API_ROOT}{API_PATH}'

TEST_CLIENT = None

if settings.TESTING:
    TEST_CLIENT = Client()

hour_range = [
    (9, 12),   # ochtend
    (13, 16),  # middag
    (17, 19),  # spits
    (20, 23),  # avond
    (0, 4),    # nacht
    (0, 23),   # dag
]

month_range = [
    # (0, 3),
    # (4, 6),
    (3, 7),
    # (10, 12),
]

day_range = [
    (0, 6),  # hele week
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
    delta = timedelta(days=90)
    today = datetime.today() - delta
    before = today - delta

    year1 = before.year
    year2 = today.year

    month1 = before.month
    # This month we have no data.
    # so we should take month before
    month2 = today.month

    return year1, year2, month1, month2


def occupancy_buckets():
    """
    Determine the occupancy buckets
    we need
    """
    buckets = []

    y1, y2, m1, m2 = make_year_month_range()

    for d1, d2 in day_range:
        for h1, h2 in hour_range:
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
    assert b.m1 <= b.m2
    assert b.d1 <= b.d2
    assert b.h1 <= b.h2

    return True


# make sure selections and weg_id are unique
# selection_road_mapping = {}


def store_occupancy_data(json, selection):

    if not json.get('wegdelen'):
        return 0

    for wd_id, wd_data in json['wegdelen'].items():

        avg_occupancy = wd_data.get('avg_occupancy')
        min_occupancy = wd_data.get('max_occupancy')
        max_occupancy = wd_data.get('min_occupancy')
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
    done_selections = Selection.objects.filter(status__isnull=1).count()

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


def do_request(selection):
    """
    Build a single request to PP api.
    """
    s = selection

    payload = {
        'year_gte': s.year1,
        'year_lte': s.year2,
        'month_gte': s.month1,
        'month_lte': s.month2 or s.month1,
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
        log.error(response.url)
        selection.status = None
        selection.save()
        raise ValueError

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


def fill_occupancy_roadparts():
    """
    Fill occupancy table with occupancy
    cijfers
    """

    work_selections = get_work_to_do()

    work_count = work_selections.count()

    for i, selection in enumerate(work_selections):
        _s = selection

        log.info(f'Working on {_s.id} {_s.view_name()}')

        response_json = do_request(selection)
        wd_count = store_occupancy_data(response_json, selection)

        log.debug(
            '%d of %d: %4s wegdelen: %d',
            i, work_count, selection._name(),
            wd_count
        )

        store_selection_status(selection)


def execute_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def create_selection_views():
    """
    Create views of selections usable for mapserver / qgis
    """

    work_done = Selection.objects.filter(status=1)

    for selection in work_done:
        view_name = selection.view_name()

        log.info('Created view %s', view_name)
        # create view for each selection with
        # geometry data.

        sql = f"""
DROP VIEW IF EXISTS sv{str(view_name)};
CREATE VIEW sv{str(view_name)} as
SELECT
    row_number() OVER (ORDER BY wd.bgt_id) as id,
    wd.bgt_id,
    wd.vakken,
    wd.fiscale_vakken,
    occupancy,
    geometrie
FROM wegdelen_wegdeel wd, occupancy_roadoccupancy oc, occupancy_selection s
WHERE wd.bgt_id = oc.bgt_id
AND wd.vakken >= 3
AND s.id = oc.selection_id
AND s.id = {selection.id}
        """
        execute_sql(sql)


def create_wegdelen_stats():

    sql = """
CREATE VIEW wegdelen_statistiek AS
SELECT
        o.bgt_id,
        wd.fiscale_vakken,
        count(*),
        AVG(occupancy),
        MIN(occupancy),
        MAX(occupancy),
        STDDEV(occupancy)
FROM occupancy_roadoccupancy o
JOIN occupancy_selection s on (s.id = o.selection_id)
JOIN wegdelen_wegdeel wd on (o.bgt_id = wd.bgt_id)
WHERE s.day1 = s.day2
GROUP BY(o.bgt_id, wd.fiscale_vakken)
    """

    execute_sql(sql)


def create_statistiek_csv():
    """
    Per wegdeel even kijken.
    """

    select = "select * from wegdelen_statistiek"
    outputquery = f"COPY ({select}) TO STDOUT WITH CSV HEADER"
    # wegdelen stats.
    with connection.cursor() as cursor:
        file_name = f'{settings.CSV_DIR}/wegdelen_stats.csv'
        with open(file_name, 'w') as f:
                log.debug('saving view: %s', file_name)
                cursor.copy_expert(outputquery, f)


def dump_csv_files():
    """
    For each view create a csv file.
    """

    work_done = Selection.objects.filter(status=1)

    create_statistiek_csv()

    for selection in work_done:
        view_name = selection.view_name()

        select = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken,
            ST_AsText(geometrie)
        FROM sv{str(view_name)}
        """

        select_no_geo = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken
        FROM sv{str(view_name)}
        """

        outputquery = f"COPY ({select}) TO STDOUT WITH CSV HEADER"
        outputquery_no_geo = f"COPY ({select_no_geo}) TO STDOUT WITH CSV HEADER"   # noqa

        file_name = f'{settings.CSV_DIR}/{str(view_name)}.csv'
        file_name_no_geo = f'{settings.CSV_DIR}/{str(view_name)}.nogeo.csv'

        with connection.cursor() as cursor:

            with open(file_name, 'w') as f:
                log.debug('saving view: %s', file_name)
                cursor.copy_expert(outputquery, f)

            with open(file_name_no_geo, 'w') as f:
                log.debug('saving view: %s', file_name_no_geo)
                cursor.copy_expert(outputquery_no_geo, f)
