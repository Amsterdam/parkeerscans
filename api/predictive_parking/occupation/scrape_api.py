"""
Load occupation from our own elastic API
in the database for easy to consume datasets
"""
import logging
import requests

from collections import namedtuple
from django.db.models import F, Count

from django.conf import settings
# from wegdelen.models import WegDeel
from wegdelen.models import Buurt
from occupation.models import RoadOccupation
from occupation.models import Selection

from django.db import connection


log = logging.getLogger(__name__)

API_URL = 'https://acc.api.data.amsterdam.nl/predictiveparking/metingen/aggregations/wegdelen/'  # noqa

hour_range = [
    (9, 12),
    (13, 16),
    (17, 19),
    (20, 23),
    # (0, 4),
    # (4, 8),
]

month_range = [
    (0, 3),
    (4, 6),
    (7, 9),
    (10, 12),
]

Bucket = namedtuple('bucket', ['m1', 'm2', 'day', 'h1', 'h2'])


def occupation_buckets():
    """
    Determine the occupation buckets
    we need
    """
    buckets = []

    for month in range(4, 10):
        for day in range(0, 7):
            for h1, h2 in hour_range:

                b = Bucket(month, month, day, h1, h2)

                buckets.append(b)

    return buckets


def create_selections(buckets):
    """
    For selection buckets
    """

    for b in buckets:

        Selection.objects.get_or_create(
            day1=b.day,
            hour1=b.h1,
            hour2=b.h2,
            month1=b.month1,
            month2=b.month2,
            year1=2016,
            year2=2017,
        )


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

    # select a part
    part = settings.SCRAPE['IMPORT_PART']
    if part:
        log.info('Doing chunck %d of 4', part)
        work_selections = (
            work_selections
            .annotate(idmod=F('id') % 4)
            .filter(idmod=part-1))

    return work_selections


def fill_occupation_roadparts():
    """
    Fill occupation table with occupation
    cijfers
    """

    work_selections = get_work_to_do()

    # determine all neigborhoods with 'payed parking spots'
    relevante_buurten = Buurt.objects.filter(fiscale_vakken__gt=0)

    for s in work_selections:

        log.info(f'Working on {s.id} {s}')

        for buurt in relevante_buurten:

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

            r = requests.get(API_URL, payload)

            if r.status_code != 200:
                raise ValueError

            store_occupation_data(r.json(), s)

        # mark this selection as done.
        s.status = 1
        s.save()

        wd_count = (
            RoadOccupation.objects.select_related()
            .filter(selection_id=s.id)
            .values_list('selection_id')
            .annotate(wdcount=Count('selection_id'))
        )
        log.info(f'Roadparts {wd_count[0][1]} for  {s}')


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
