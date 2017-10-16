"""
Load occupation from our own elastic API
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
# from wegdelen.models import WegDeel
from wegdelen.models import Buurt
from occupation.models import RoadOccupation
from occupation.models import Selection


log = logging.getLogger(__name__)


API_URL = 'https://acc.api.data.amsterdam.nl/predictiveparking/metingen/aggregations/wegdelen/'  # noqa

hour_range = [
    (9, 12),   # ochtend
    (13, 16),  # middag
    (17, 19),  # spits
    (20, 23),  # avond
    # (0, 4),
    (0, 23),
]

month_range = [
    # (0, 3),
    # (4, 6),
    (6, 10),
    # (10, 12),
]

day_range = [
    (0, 6),  # hele week
    (0, 4),  # werkdag
    (5, 6),  # weekend
]

year_range = [
    (2017, 2017),
]

Bucket = namedtuple(
    'bucket', ['y1', 'y2', 'm1', 'm2', 'd1', 'd2', 'h1', 'h2'])


def make_year_month_range():
    """
    now - 3 months
    """
    today = datetime.today()
    delta = timedelta(days=90)
    before = today - delta

    year1 = before.year
    year2 = today.year

    month1 = before.month
    # this month we have no data.
    # so we should take month before
    month2 = today.month - 1

    return year1, year2, month1, month2


def occupation_buckets():
    """
    Determine the occupation buckets
    we need
    """
    buckets = []

    y1, y2, m1, m2 = make_year_month_range()

    for d1, d2 in day_range:
        for h1, h2 in hour_range:

            b = Bucket(y1, y2, m1, m2, d1, d2, h1, h2)

            buckets.append(b)

    return buckets


def create_selections(buckets):
    """
    For selection buckets
    """

    for b in buckets:

        Selection.objects.get_or_create(
            day1=b.d1,
            day2=b.d2,
            hour1=b.h1,
            hour2=b.h2,
            month1=b.m1,
            month2=b.m2,
            year1=b.y1,
            year2=b.y2,
        )


def create_single_selection(longstring):
    """
    Create a manual selection

    validate input..
    """
    manual_selection = longstring.split(':')
    assert len(manual_selection) == 8
    y1, y2, m1, m2, d1, d2, h1, h2 = map(int, manual_selection)
    # lets do some validation..
    assert min(manual_selection) >= 0
    assert y1 in range(2016, 2025)
    assert y2 in range(2016, 2025)
    assert m1 in range(0, 12)
    assert m2 in range(0, 12)
    assert d1 in range(0, 7)
    assert d2 in range(0, 7)
    assert h1 in range(0, 24)
    assert h2 in range(0, 24)
    assert y1 <= y2
    assert m1 <= m2
    assert d1 <= d2
    assert y1 <= y2
    assert h1 <= h2

    # add the new selection
    b = Bucket(*manual_selection)
    create_selections([b])


# make sure selections and weg_id are unique
# selection_road_mapping = {}


def store_occupation_data(json, selection):

    for wd_id, wd_data in json['wegdelen'].items():

        if not wd_data.get('occupation'):
            # no occupation ?
            # parking sport dissapeared?
            continue

        r, created = RoadOccupation.objects.get_or_create(
            bgt_id=wd_id,
            selection=selection,
        )

        # float fields elastic - postgres are different
        # so get_or_create will not work
        if created is False:
            continue
        else:
            r.occupation = wd_data['occupation']
            r.save()


def create_selection_buckets():
    buckets = occupation_buckets()
    create_selections(buckets)


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


def do_request(selection, buurt):
    """
    Build a single request to PP api.
    """
    s = selection

    payload = {
        'year_gte': s.year1,
        'year_lte': s.year2,
        'month': s.month1,
        'month_gte': s.month1,
        'month_lte': s.month2 or s.month1,
        'day': s.day1,
        'hour_gte': s.hour1,
        'hour_lte': s.hour2,
        'buurtcode': buurt.code,
    }

    response = requests.get(API_URL, payload)

    if response.status_code != 200:
        selection.status = None
        selection.save()
        raise ValueError

    return response


def store_selection_status(selection):
    """
    Given selection
    """
    wd_count = (
        RoadOccupation.objects.select_related()
        .filter(selection_id=selection.id)
        .values_list('selection_id')
        .annotate(wdcount=Count('selection_id'))
    )

    # mark this selection as done.
    selection.status = 1
    selection.save()

    if len(wd_count):
        log.info(f'Roadparts {wd_count[0][1]} for {selection}')


def fill_occupation_roadparts():
    """
    Fill occupation table with occupation
    cijfers
    """

    work_selections = get_work_to_do()

    # determine all neigborhoods with 'payed parking spots'
    relevante_buurten = Buurt.objects.filter(fiscale_vakken__gt=0)

    buurt_count = relevante_buurten.count()
    work_count = work_selections.count()

    for selection in work_selections:
        _s = selection
        log.info(f'Working on {_s.id} {_s.view_name()}')

        for i, buurt in enumerate(relevante_buurten):

            log.debug(
                '%d %d/%d : %4s %s',
                work_count, i, buurt_count,
                buurt.code, selection._name())

            # do parallel requests
            response = do_request(selection, buurt)
            store_occupation_data(response.json(), selection)

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
CREATE OR REPLACE VIEW sv{str(view_name)} as
SELECT wd.bgt_id, occupation, geometrie
FROM wegdelen_wegdeel wd, occupation_roadoccupation oc, occupation_selection s
WHERE wd.bgt_id = oc.bgt_id
AND s.id = oc.selection_id
AND s.id = {selection.id}
        """
        execute_sql(sql)
