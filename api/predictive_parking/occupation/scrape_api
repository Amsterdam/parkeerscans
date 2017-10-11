"""
Load occupation from our own elastic API
in the database for easy to consume datasets
"""

from wegdelen.models import Wegdeel

API_URL = 'https://api.data.amsterdam.nl/predictiveparking/metingen/wegdelen/'

hour_range = [
    (0, 4),
    (4, 8),
    (9, 12),
    (13, 16),
    (17, 19),
    (20, 22),
    (23, 24),
]


def occupation_buckets():
    """
    Determine the occupation buckets
    we need
    """

    buckets = []

    for month in range(0, 12):
        for day in range(0, 7):
            for h1, h2 in hour_range:
                buckets.append(month, day, h1, h2)

    return buckets


def fill_task_list(buckets):
    """
    For each roadpart with more then 3 parkingspots
    make a task
    """

    tasks = []

    for bgt_id in Wegdeel.objects.filter(
            fiscale_vakken__gt=3).value_list('bgt_id'):
        for job in buckets:
            task = list(job)
            task.append(bgt_id)

    return tasks


def fill_occupation_roadparts():
    """
    """
    buckets = occupation_buckets()
    tasks = fill_task_list(buckets)

    print(len(tasks))
