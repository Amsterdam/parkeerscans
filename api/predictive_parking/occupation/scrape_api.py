"""
Load occupation from our own elastic API
in the database for easy to consume datasets
"""
import logging

from collections import namedtuple

# from wegdelen.models import WegDeel
from wegdelen.models import Buurt

from occupation.models import RoadOccupation
from occupation.models import Selection

import requests

log = logging.getLogger(__name__)

API_URL = 'https://api.datapunt.amsterdam.nl/predictiveparking/metingen/aggregations/wegdelen/'  # noqa

hour_range = [
    (17, 19),
    (9, 12),
    (13, 16),
    (20, 23),
    # (0, 4),
    # (4, 8),
]

Bucket = namedtuple('bucket', ['month', 'day', 'h1', 'h2'])


def occupation_buckets():
    """
    Determine the occupation buckets
    we need
    """
    buckets = []

    for month in range(4, 10):
        for day in range(0, 7):
            for h1, h2 in hour_range:

                b = Bucket(month, day, h1, h2)

                buckets.append(b)

    return buckets


def create_selections(buckets):
    """
    For selection buckets
    """

    for b in buckets:

        Selection.objects.update_or_create(
            day1=b.day,
            hour1=b.h1,
            hour2=b.h2,
            month1=b.month,
            year1=2016,
            year2=2017,
        )


# make sure selections and weg_id are unique
# selection_road_mapping = {}


def store_occupation_data(json, selection):

    for wd_id, wd_data in json['wegdelen'].items():

        if not wd_data.get('occupation'):
            continue

        r, created = RoadOccupation.objects.get_or_create(
            bgt_id=wd_id,
            selection=selection,
        )
        # float fields elastic - postgres are different
        if created is False:
            continue
        else:
            r.occupation = wd_data['occupation']
            r.save()


def create_selection_buckets():
    buckets = occupation_buckets()
    create_selections(buckets)


def fill_occupation_roadparts():
    """
    Fill occupation table with occupation
    cijfers
    """

    relevante_buurten = Buurt.objects.filter(fiscale_vakken__gt=0)
    all_selections = Selection.objects.all()

    for buurt in relevante_buurten:

        for s in all_selections:

            payload = {
                'year_gte': s.year1,
                'year_lte': s.year2,
                'month': s.month1,
                'day': s.day1,
                'hour_gte': s.hour1,
                'hour_lte': s.hour2,
                'buurtcode': buurt.code,
            }

            r = requests.get(API_URL, payload)

            if r.status_code != 200:
                raise ValueError

            store_occupation_data(r.json(), s)
