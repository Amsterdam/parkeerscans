"""
We use the objectstore to get the latest and greatest of the mks dump
"""

import re
import os
import logging
from pathlib import Path

from swiftclient.client import Connection

from dateutil import parser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)

assert os.getenv('PARKEERVAKKEN_OBJECTSTORE_PASSWORD')

DATE_RE = re.compile('\d\d\d\d\d\d')

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


def full_file_list():

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
    return rars_sorted_by_time


def get_latest_rarfiles():
    """
    Get latest rarfile
    """
    rars_sorted_by_time = full_file_list()

    rar_files = []
    start_month = None

    if os.getenv('STARTDATE'):
        start_month = int(os.getenv('STARTDATE'))

    log.debug('START_MONTH: %s', start_month)

    for time, object_meta_data in rars_sorted_by_time:
        rarname = object_meta_data['name'].split('/')[-1]

        if 'totaal' not in rarname and '2017' not in rarname:

            log.debug('skiped %s', rarname)
            continue

        if start_month:
            m = DATE_RE.findall(rarname)
            if m:
                file_month = int(m[0])
                if file_month < start_month:
                    log.debug('skiped %s, too old', rarname)
                    continue

        rar_files.append((time, object_meta_data))

    return rar_files


def download_files(rar_files):

    for time, object_meta_data in rar_files:

        rarname = object_meta_data['name'].split('/')[-1]
        file_location = '{}/{}'.format(DATA_DIR, rarname)

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


if __name__ == '__main__':
    # get_parkeerkans_db_dumps()
    rar_files_to_download = get_latest_rarfiles()
    download_files(rar_files_to_download)
