
import logging
import sys
import glob

from django.core.management import BaseCommand
from scans.models import Scan
from logdecorator import LogWith

import import_scans

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Import/Modify table data from csv

    clear data using:

    - manage.py migrate bbga_data zero
    - manage.py migrate bbga_data

    """

    def add_arguments(self, parser):

        parser.add_argument(
            '--scans',
            action='store_true',
            dest='scans',
            default=False,
            help='inladen scans')

        parser.add_argument(
            '--fixgeometrie',
            action='store_true',
            dest='scans',
            default=False,
            help='maken geometrie')

        parser.add_argument(
            '--fixbgt',
            action='store_true',
            dest='wegdelen',
            default=False,
            help='link scans met wegdelen')

        parser.add_argument(
            '--fixvakken',
            action='store_true',
            dest='vakken',
            default=False,
            help='link scans met parkeerplaatsen')

    @LogWith(log)
    def handle(self, *args, **options):
        """
        Validate and execute import task
        """

        scan_csvs = glob.glob('unzipped/*.csv')
        table = Scan._meta.db_table

        if options['scans']:
            print('Implemented in golang..')
            return
            # import csv
            Scan.objects.all().delete()
            for csv in scan_csvs:
                import_scans.import_scans_csv(csv, table)
        elif options['geometry']:
                import_scans.set_geometry_field()
        elif options['wegdelen']:
                raise NotImplementedError
        elif options['vakken']:
                raise NotImplementedError
        else:
            log.error('Nothing imported.')
            sys.exit(1)
