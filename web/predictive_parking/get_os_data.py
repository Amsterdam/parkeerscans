"""
We use the objectstore to get the latest and greatest of the mks dump
"""

import os
import logging
from pathlib import Path

from swiftclient.client import Connection

from dateutil import parser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

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


DATA_DIR = '/app/data/'

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


def get_latest_zipfile():
    """
    Get latest zipfile uploaded by mks
    """
    zip_list = []

    meta_data = get_full_container_list(
        parkeren_conn, 'predictive')

    for o_info in meta_data:
        if o_info['content_type'] in [
                'application/rar', 'application/zip']:
            dt = parser.parse(o_info['last_modified'])
            zip_list.append((dt, o_info))

    zips_sorted_by_time = sorted(zip_list)

    for time, object_meta_data in zips_sorted_by_time:
        zipname = object_meta_data['name'].split('/')[-1]
        file_location = '{}/{}'.format(DATA_DIR, zipname)

        if file_exists(file_location):
            # Already downloaded
            log.debug('skiped %s', file_location)
            continue

        # Download all not missing data
        zipname = object_meta_data['name'].split('/')[-1]
        log.info('Downloading: %s %s', time, zipname)
        latest_zip = get_store_object(object_meta_data)

        # save output to file!
        with open('{}/{}'.format(DATA_DIR, zipname), 'wb') as outputzip:
            outputzip.write(latest_zip)

get_latest_zipfile()
