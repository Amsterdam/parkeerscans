from django.db import connection
import psycopg2
import logging

from django.conf import settings

from occupancy.models import Selection


log = logging.getLogger(__name__)   # noqa


def execute_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def create_selection_tables():
    """
    Create tables of selections usable for mapserver / qgis

    We make tables for ease of dumping / restoring tables
    """

    work_done = Selection.objects.filter(status=1)

    for selection in work_done:
        view_name = selection.view_name()

        log.info('Created view %s', view_name)
        # create view for each selection with
        # geometry data.

        sql = f"""
DROP TABLE IF EXISTS sv{str(view_name)};
SELECT * INTO sv{str(view_name)} FROM (
SELECT
    row_number() OVER (ORDER BY wd.bgt_id) as id,
    wd.bgt_id,
    wd.vakken,
    wd.fiscale_vakken,
    occupancy,
    min_occupancy,
    max_occupancy,
    std_occupancy, unique_scans,
    b.code,
    wd.geometrie
FROM wegdelen_wegdeel wd, occupancy_roadoccupancy oc,
     occupancy_selection s, wegdelen_buurt b
WHERE wd.bgt_id = oc.bgt_id
AND ST_Contains(b.geometrie, wd.geometrie)
AND wd.vakken >= 3
AND s.id = oc.selection_id
AND s.id = {selection.id}) as tmptable
        """
        execute_sql(sql)


def dump_csv_files():
    """
    For each view create a csv file.
    """

    work_done = Selection.objects.filter(status=1)

    for selection in work_done:
        view_name = selection.view_name()

        select = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken,
            min_occupancy, max_occupancy, std_occupancy, unique_scans,
            code,
            ST_AsText(geometrie)
        FROM sv{str(view_name)}
        """

        select_no_geo = f"""
        SELECT
            id, bgt_id, occupancy, vakken, fiscale_vakken
            min_occupancy, max_occupancy, std_occupancy, unique_scans,
            code
        FROM sv{str(view_name)}
        """

        outputquery = f"COPY ({select}) TO STDOUT WITH CSV HEADER"
        outputquery_no_geo = f"COPY ({select_no_geo}) TO STDOUT WITH CSV HEADER"   # noqa

        file_name = f'{settings.CSV_DIR}/{str(view_name)}.csv'
        file_name_no_geo = f'{settings.CSV_DIR}/{str(view_name)}.nogeo.csv'

        with connection.cursor() as cursor:

            try:
                with open(file_name, 'w') as csvfile:
                    log.debug('saving view: %s', file_name)
                    cursor.copy_expert(outputquery, csvfile)

                with open(file_name_no_geo, 'w') as csvfile:
                    log.debug('saving view: %s', file_name_no_geo)
                    cursor.copy_expert(outputquery_no_geo, csvfile)

            except psycopg2.ProgrammingError:
                log.exception('table missing')
