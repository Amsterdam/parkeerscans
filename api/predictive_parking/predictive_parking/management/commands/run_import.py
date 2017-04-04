"""
Import commands
"""

import logging
import sys

from django.core.management import BaseCommand

import import_wegdelen

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
            '--setunlogged',
            action='store_true',
            dest='unlogged',
            default=False,
            help='set scan tables unlogged decreases diskwrites')

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
            '--cluster',
            action='store_true',
            dest='cluster',
            default=False,
            help='cluster geoindexen')

        parser.add_argument(
            '--scanmomentindex',
            action='store_true',
            dest='scanmoment',
            default=False,
            help='scanmoment index')

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

        parser.add_argument(
            '--addwegdeeltowrongscans',
            action='store_true',
            dest='mergewegdelennzonderpv',
            default=False,
            help='merge scans met wegdelen als deze geen parkeerid hebben')

        parser.add_argument(
            '--storescantables',
            action='store_true',
            dest='findscantables',
            default=False,
            help='create list of scanstables')

        parser.add_argument(
            '--addsummaryscancounts',
            action='store_true',
            dest='summarycounts',
            default=False,
            help='Add summary counts to wegdelen en vakken')

    def handle(self, *args, **options):
        """
        Validate and execute import task
        """

        if options['wegdelen']:
            import_wegdelen.import_wegdelen()
        elif options['unlogged']:
            import_wegdelen.make_scans_unlogged()
        elif options['vakken']:
            # Convert to wgs84
            import_wegdelen.import_parkeervakken()
        elif options['buurten']:
            import_wegdelen.import_buurten()
        elif options['cluster']:
            import_wegdelen.cluster_geometrieindexen()
        elif options['scanmoment']:
            import_wegdelen.scan_moment_index()
        elif options['mergewegdelen']:
            import_wegdelen.add_wegdeel_to_parkeervak(distance=0.00001)
        elif options['mergebuurten']:
            import_wegdelen.add_buurt_to_parkeervak()
        elif options['setcounts']:
            import_wegdelen.add_parkeervak_count_to_buurt()
            import_wegdelen.add_parkeervak_count_to_wegdeel()
        elif options['findscantables']:
            import_wegdelen.collect_scans_table_list()
        elif options['summarycounts']:
            import_wegdelen.add_scan_count_wegdelen_vakken()
        else:
            log.error('Nothing imported.')
            sys.exit(1)
