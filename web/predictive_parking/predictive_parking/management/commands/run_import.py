
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
            '--wegdelen',
            action='store_true',
            dest='wegdelen',
            default=False,
            help='link scans met wegdelen')

        parser.add_argument(
            '--vakken',
            action='store_true',
            dest='vakken',
            default=False,
            help='link scans met parkeerplaatsen')

        parser.add_argument(
            '--mergewegdelen',
            action='store_true',
            dest='mergewegdelen',
            default=False,
            help='link wegdelen met parkeerplaatsen')

        parser.add_argument(
            '--mergevakken',
            action='store_true',
            dest='mergevakken',
            default=False,
            help='link parkeervakken met scans')

    def handle(self, *args, **options):
        """
        Validate and execute import task
        """

        if options['wegdelen']:
            import_scans.import_wegdelen()
        elif options['vakken']:
            # Convert to wgs84
            import_scans.import_parkeervakken()
        elif options['mergewegdelen']:
            import_scans.add_wegdeel_to_parkeervak()
        elif options['mergevakken']:
            import_scans.add_parkeervak_to_scans()
        elif options['normalizescans']:
            # Add vakken en wegdelen informatie aan scans
            # import_scans.add_parkeervak_to_scans()
            raise NotImplementedError
        else:
            log.error('Nothing imported.')
            sys.exit(1)
