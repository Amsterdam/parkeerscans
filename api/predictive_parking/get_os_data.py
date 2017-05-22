"""
We use the objectstore to get the latest and greatest of the mks dump
"""

import os
import logging
from pathlib import Path

from swiftclient.client import Connection

from dateutil import parser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)

assert os.getenv('PARKEERVAKKEN_OBJECTSTORE_PASSWORD')


OBJECTSTORE = dict(
    VERSION='2.0',
    AUTHURL='https://identity.stack.cloudvps.com/v2.0',
    TENANT_NAME='BGE000081_Parkeren',
    TENANT_ID='fd380ccb48444960837008800a453122',
    USER='parkeren',
    PASSWORD=os.getenv('PARKEERVAKKEN_OBJECTSTORE_PASSWORD'),
    REGION_NAME='NL',
)


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("swiftclient").setLevel(logging.WARNING)


DATA_DIR = '/app/data'
# DATA_DIR = '/tmp/data'

store = OBJECTSTORE

parkeren_conn = Connection(
    authurl=store['AUTHURL'],
    user=store['USER'],
    key=store['PASSWORD'],
    tenant_name=store['TENANT_NAME'],
    auth_version=store['VERSION'],
    os_options={'tenant_id': store['TENANT_ID'],
                'region_name': store['REGION_NAME']})


def get_store_object(object_meta_data):
    return parkeren_conn.get_object(
        'predictive', object_meta_data['name'])[1]


def get_full_container_list(conn, container, **kwargs):
    limit = 10000
    kwargs['limit'] = limit
    page = []

    seed = []

    _, page = conn.get_container(container, **kwargs)
    seed.extend(page)

    while len(page) == limit:
        # keep getting pages..
        kwargs['marker'] = seed[-1]['name']
        _, page = conn.get_container(container, **kwargs)
        seed.extend(page)

    return seed


def file_exists(target):
    target = Path(target)
    return target.is_file()


def get_latest_rarfile():
    """
    Get latest rarfile
    """
    rar_list = []

    meta_data = get_full_container_list(
        parkeren_conn, 'predictive')

    for o_info in meta_data:
        if o_info['content_type'] in [
                'application/octet-stream',
                'application/rar']:
            dt = parser.parse(o_info['last_modified'])
            rar_list.append((dt, o_info))

    rars_sorted_by_time = sorted(rar_list)

    for time, object_meta_data in rars_sorted_by_time:
        rarname = object_meta_data['name'].split('/')[-1]
        file_location = '{}/{}'.format(DATA_DIR, rarname)

        if 'totaal' not in rarname and '2017' not in rarname:
            log.debug('skiped %s', rarname)
            continue

        if file_exists(file_location):
            # Already downloaded
            log.debug('skiped %s', file_location)
            continue

        # Download all not missing data
        rarname = object_meta_data['name'].split('/')[-1]
        log.info('Downloading: %s %s', time, rarname)
        latest_zip = get_store_object(object_meta_data)

        # save output to file!
        with open('{}/{}'.format(DATA_DIR, rarname), 'wb') as outputzip:
            outputzip.write(latest_zip)


def get_parkeerkans_db_dumps():
    """
    Find database dumps
    """

    meta_data = get_full_container_list(
        parkeren_conn, 'predictive')

    for object_meta_data in meta_data:

        if not object_meta_data['name'].startswith('parkeerkans'):
            continue

        if object_meta_data['content_type'] not in [
                'application/octet-stream',
                'application/rar']:
            continue

        dumpname = object_meta_data['name'].split('/')[-1]
        dt = parser.parse(object_meta_data['last_modified'])
        log.info('Downloading: %s %s', dt, dumpname)
        pg_dump_file = get_store_object(object_meta_data)

        with open('{}/{}.dump'.format(DATA_DIR, dumpname), 'wb') as output:
            output.write(pg_dump_file)


get_parkeerkans_db_dumps()
get_latest_rarfile()
