
import logging
import sys

from django.core.management import BaseCommand

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
            help='importeer wegdelen uit bgt')

        parser.add_argument(
            '--vakken',
            action='store_true',
            dest='vakken',
            default=False,
            help='importeer parkeervakken uit parkeervakken ')

        parser.add_argument(
            '--buurten',
            action='store_true',
            dest='buurten',
            default=False,
            help='importeer buurten uit bag')

        parser.add_argument(
            '--parkeervakcounts',
            action='store_true',
            default=False,
            dest='setcounts',
            help='add parkeervak counts aan buurten en wegdelen')

        parser.add_argument(
            '--mergewegdelen',
            action='store_true',
            dest='mergewegdelen',
            default=False,
            help='merge wegdelen met parkeerplaatsen')

        parser.add_argument(
            '--mergebuurten',
            action='store_true',
            dest='mergebuurten',
            default=False,
            help='merge buurten met parkeerplaatsen')

        parser.add_argument(
            '--mergevakken',
            action='store_true',
            dest='mergevakken',
            default=False,
            help='merge scans met parkeervakken')

    def handle(self, *args, **options):
        """
        Validate and execute import task
        """

        if options['wegdelen']:
            import_scans.import_wegdelen()
        elif options['vakken']:
            # Convert to wgs84
            import_scans.import_parkeervakken()
        elif options['buurten']:
            import_scans.import_buurten()
        elif options['mergewegdelen']:
            import_scans.add_wegdeel_to_parkeervak()
        elif options['mergebuurten']:
            import_scans.add_buurt_to_parkeervak()
        elif options['setcounts']:
            import_scans.add_parkeervak_count_to_buurt()
            import_scans.add_parkeervak_count_to_wegdeel()
        elif options['mergevakken']:
            import_scans.add_parkeervak_to_scans()
        elif options['normalizescans']:
            # Add vakken en wegdelen informatie aan scans
            # import_scans.add_parkeervak_to_scans()
            raise NotImplementedError
        else:
            log.error('Nothing imported.')
            sys.exit(1)
