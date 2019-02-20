"""
We use the objectstore to get the latest and greatest of the mks dump
"""

import re
import isoweek
import os
import json
import logging
from pathlib import Path

from swiftclient.client import Connection
from swiftclient.exceptions import ClientException

from dateutil import parser

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)

DATE_RE = re.compile('\d\d\d\d\d\d')
YEAR_RE = re.compile('\d\d\d\d')
WEEK_RE = re.compile('.*(week)([0-9]+).*')

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
    os_options={
        'tenant_id': store['TENANT_ID'],
        'region_name': store['REGION_NAME']}
    )


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


def should_we_download_this(rarname: str, start_month: int, end_month: int, handled_files: set) -> bool:
    """
    Check if we should download this rar files

    we do checks on age
    """
    file_month = None
    # 2018 names
    year = YEAR_RE.findall(rarname)
    week = WEEK_RE.match(rarname)

    if year and week:
        weeknr = int(week.groups()[1])
        w = isoweek.Week(int(year[0]), weeknr)
        d = w.monday()
        file_month = int('%d%02d' % (d.year, d.month))

    else:
        # 2017 names
        m = DATE_RE.findall(rarname)
        if m:
            file_month = int(m[0])

    if not file_month:
        log.debug('date not parsed from file name: %s', rarname)
        return False

    if start_month:
        if file_month < start_month:
            log.debug('skipped %s, too old', rarname)
            return False
    if end_month:
        if file_month >= end_month:
            log.debug('skipped %s, too new', rarname)
            return False

    if rarname in handled_files:
        log.debug('skipped %s file previously added', rarname)
        return False

    return True


def get_latest_rarfiles(storage):
    """
    Get latest rarfile
    """
    rars_sorted_by_time = full_file_list()

    rar_files = []
    start_month = None
    end_month = None

    if os.getenv('STARTDATE'):
        # 201708
        start_month = int(os.getenv('STARTDATE'))
    if os.getenv('ENDDATE'):
        # 201708
        end_month = int(os.getenv('ENDDATE'))

    handled_files = storage.load_handled_files()

    log.debug('STARTDATE: %s', start_month)
    log.debug('ENDDATE: %s', end_month)

    for time, object_meta_data in rars_sorted_by_time:
        full_name = object_meta_data['name']
        rarname = full_name.split('/')[-1]

        if 'oud' in full_name:
            log.debug('too old %s', rarname)
            continue

        # no selection given. do everything.
        if not start_month and not end_month:
            rar_files.append((time, object_meta_data))

        # given selection pick rar files.
        if should_we_download_this(rarname, start_month, end_month, handled_files):
            rar_files.append((time, object_meta_data))

    return rar_files


def download_files(rar_files, storage):

    for time, object_meta_data in rar_files:

        rarname = object_meta_data['name'].split('/')[-1]
        file_location = '{}/{}'.format(DATA_DIR, rarname)

        if file_exists(file_location):
            # Already downloaded
            log.debug('already downloaded %s', file_location)
            continue

        # Download all not missing data
        rarname = object_meta_data['name'].split('/')[-1]
        log.info('Downloading: %s %s', time, rarname)
        latest_zip = get_store_object(object_meta_data)

        # save output to file!
        with open('{}/{}'.format(DATA_DIR, rarname), 'wb') as outputzip:
            outputzip.write(latest_zip)

    #TODO discuss if there is better place, moment within the ETL process
    #Files are stored but not yet processed added in the database.
    cleaned_names = (parse_name(i['name']) for _, i in rar_files)
    storage.save_handled_files(cleaned_names)


def parse_name(full_name):
    return full_name.split('/')[-1]


class StoreObjectStorage:
    def __init__(self, filename='handled_files', connection=None, container_name=None):
        self.filename = filename
        self.container_name = container_name
        self.connection = connection
        self.whitelisted = [
            'datapunt_import_status/test',
            'datapunt_import_status/acceptance',
            'datapunt_import_status/production',
        ]

        assert self.container_name is not None

    def load(self, container_name=None, filename=None):
        try:
            return self.connection.get_object(container_name or self.container_name, filename or self.filename)
        except ClientException:
            raise

    def save(self, data, container_name=None, filename=None):
        self.connection.put_object(container_name or self.container_name, filename or self.filename, data)

    def save_handled_files(self, file_names, filename=None):
        """To save the new set of files, combined them with previous seen files."""
        assert self.container_name in self.whitelisted

        prev_files = self.load_handled_files(filename=filename, suppress=True)
        combined_files = prev_files.union(set(file_names))
        json_files = json.dumps({'files': list(combined_files)})
        try:
            self.save(json_files, self.container_name, filename or self.filename)
        except ClientException:
            log.warning("Failed to save file")

    def load_handled_files(self, filename=None, suppress=False):
        assert self.container_name in self.whitelisted

        try:
            item = self.load(self.container_name, filename or self.filename)
            return set(json.loads(item[1].decode('utf-8'))['files'])
        except ClientException:
            if not suppress:
                log.warning('Exception during connection with object storage, previously handled files are not skipped')
            return set()
        except (json.decoder.JSONDecodeError, ValueError):
            log.warning(
                'Exception parsing obj storage response, previously handled files are not skipped')
            return set()


if __name__ == '__main__':
    # get_parkeerkans_db_dumps()
    assert os.getenv('PARKEERVAKKEN_OBJECTSTORE_PASSWORD')
    if os.getenv('HANDLED_FILES_ENV') is None:
        log.warning("HANDLED_FILES_ENV not set, previous loaded files are not skipped")

    storage = StoreObjectStorage(
        filename='handled_files',
        container_name= os.getenv('HANDLED_FILES_ENV') or 'datapunt_import_status/test',
        connection=parkeren_conn
    )
    rar_files_to_download = get_latest_rarfiles(storage)
    download_files(rar_files_to_download, storage)

