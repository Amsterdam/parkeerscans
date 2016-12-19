"""
Import scans
"""
import logging


    

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)


def import_scans_csv(csv_file, table):
    """
    Import the large weekly scans dataset
    """
    log.debug('removing old variable data')
    # clear old data for week x?
    # Cijfers.objects.all().delete()

    columns = ['jaar', 'gebiedcode15', 'variabele', 'waarde']
    columns = ['id' 'scan_moment', 'scan_source',
               'longitude', 'latitude', 'buurtcode',
               'afstand', 'sperscode', 'qualCode',
               'FF_DF', 'NHA_nr',  'NHA_hoogte', 'uitval_nachtrun']

    sql_statement = """
    COPY {} ({})
    FROM STDIN
    WITH
    CSV
    DELIMITER ';'
    HEADER
    """.format(table, ", ".join(columns))

    log.debug('loading new variable data')

    with connection.cursor() as c:
        with open(csv_file, 'r') as open_file:
            c.copy_expert(sql_statement, open_file)
