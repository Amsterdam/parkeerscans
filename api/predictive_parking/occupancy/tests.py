import subprocess

import logging
# import json
from django import db
from django.core.management import call_command

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse


from metingen.models import Scan
from wegdelen.models import Buurt
from wegdelen.models import WegDeel
from .models import RoadOccupancy
from .models import Selection

log = logging.getLogger(__name__)


class OccupancyTestCase(APITestCase):
    """
    Test some occupancy
    """

    @classmethod
    def setUpClass(cls):
        """
        This django app is merely a viewer on data
        we load testdata into database using special created
        test data around the silodam area.

        NOTE TEST ELASTIC MUST BE PREPARED

        read/run docker-test.sh
        """
        # we load some external testdata
        bash_command = "bash testdata/loadtestdata.sh"

        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)

        output, _error = process.communicate()

        log.debug(output)

        # reset connection
        db.connections.close_all()

        log.debug(
            'Wegdelen loaded: %d',
            WegDeel.objects.all().count())

        log.debug(
            'Buurt loaded: %d',
            Buurt.objects.all().count())
        # run the management commands.

    @classmethod
    def tearDownClass(cls):
        """
        Destroy old stuff
        """
        Scan.objects.all().delete()
        WegDeel.objects.all().delete()
        Buurt.objects.all().delete()
        RoadOccupancy.objects.all().delete()
        Selection.objects.all().delete()

    def valid_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'application/json', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_creations_of_selections(self):

        call_command(
            'scrape_occupancy', '--selections',
            verbosity=0, interactive=False)

        from .scrape_api import hour_range
        from .scrape_api import month_range
        from .scrape_api import day_range
        from .scrape_api import year_range

        count = len(hour_range) * len(month_range) \
            * len(day_range) * len(year_range)

        self.assertEqual(
            Selection.objects.count(), count)
        # cleanup
        Selection.objects.all().delete()

    def test_scrape_local_api(self):
        # add manual selection

        call_command(
            'scrape_occupancy', '--addselection',
            # find all scans in test data..
            '2016:2020:0:11:0:6:0:21',
            verbosity=0, interactive=False)

        self.assertEqual(
            Selection.objects.count(), 1)

        # scrape the selection
        call_command(
            'scrape_occupancy', '--wegdelen',
            verbosity=0, interactive=False)
        # we schould find 13 roads with an occupation
        self.assertTrue(RoadOccupancy.objects.count() >= 13)

    def test_occupancy(self):
        occ_url = reverse('occupancy-list')
        response = self.client.get(occ_url)
        self.valid_response(occ_url, response)
        # self.assertEqual(response.data['count'], 100)
        # self.assertNotEqual(response.data['count'], 101)
