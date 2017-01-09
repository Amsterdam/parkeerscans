"""
Import scans
"""
import logging
import io

# from collections import OrderedDict
# from django.conf import settings
from django.db import connection
# rom django.db.utils import DataError

# from scans.models import Scan

from logdecorator import LogWith


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)


@LogWith(log)
def import_scans_csv(csv_file, table):
    """
    Import the large weekly scans dataset

    """
    # clear old data for week x?
    # Cijfers.objects.all().delete()
    log.debug('Loading %s', csv_file)

    columns = ['scan_id', 'scan_moment', 'scan_source',
               'longitude', 'latitude', 'buurtcode',
               'afstand', 'sperscode', 'qualcode',
               'ff_df', 'nha_nr',  'nha_hoogte', 'uitval_nachtrun']

    sql_statement = """
    COPY {} ({})
    FROM STDIN
    WITH
    CSV
    DELIMITER ';'
    HEADER
    """.format(table, ", ".join(columns))

    with connection.cursor() as c:
        with open(csv_file, 'r') as open_file:
            c.copy_expert(sql_statement, open_file)


@LogWith(log)
def set_geometry_field():
    """
    Convert the lat - long fields to geometry
    """

    log.debug('Set field geometry..')
    with connection.cursor() as c:
        c.execute("""
    UPDATE scans_scan
    SET geometrie = ST_SetSRID(
        ST_MakePoint(longitude, latitude), 4326)
    WHERE geometrie is null;
    """)
