import logging
import json
import subprocess

# Packages
from rest_framework.test import APITestCase

from django import db

from metingen.models import Scan
from wegdelen.models import WegDeel, Parkeervak

log = logging.getLogger(__name__)


def pretty_data(data):
    return json.dumps(data, indent=4, sort_keys=True)


class BrowseDatasetsTestCase(APITestCase):
    """
    Verifies that browsing the API works correctly.
    """

    datasets = [
        'predictiveparking/metingen/scans',
        'predictiveparking/wegdelen',
        'predictiveparking/vakken',
    ]

    extra_endpoints = [
        'predictiveparking/voutevakken',
        'predictiveparking/voutevakken?buurt=W12b&aantal=2',
        'predictiveparking/gratis',
        'predictiveparking/gratis?type=all',
    ]

    @classmethod
    def setUpClass(cls):
        """
        This django app is merely a viewer on data
        we load testdata into database using special created
        test data around the silodam area.
        """
        # we load some external testdata
        bash_command = "bash testdata/loadtestdata.sh"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)

        output, _error = process.communicate()

        log.debug(output)
        db.connections.close_all()

    @classmethod
    def tearDownClass(cls):
        Scan.objects.all().delete()
        WegDeel.objects.all().delete()
        Parkeervak.objects.all().delete()

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

    def valid_html_response(self, url, response):
        """
        Helper method to check common status/json
        """

        self.assertEqual(
            200, response.status_code,
            'Wrong response code for {}'.format(url))

        self.assertEqual(
            'text/html; charset=utf-8', response['Content-Type'],
            'Wrong Content-Type for {}'.format(url))

    def test_lists(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            self.valid_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))
            self.assertNotEqual(
                response.data['count'],
                0, 'Wrong result count for {}'.format(url))

    def test_details(self):
        for url in self.datasets:
            response = self.client.get('/{}/'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.valid_response(url, detail)

            # self.assertIn('_display', detail.data)

    def test_lists_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            self.valid_html_response(url, response)

            self.assertIn(
                'count', response.data, 'No count attribute in {}'.format(url))

            self.assertNotEqual(
                response.data['count'],
                0, 'Wrong result count for {}'.format(url))

    def test_root_view(self):
        url = '/predictiveparking/?format=api'
        response = self.client.get(url)
        self.valid_html_response(url, response)

    def test_details_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.valid_html_response(url, detail)

            # self.assertIn('_display', detail.data)

    def test_extra_endpoints(self):
        """
        We have build some custom data validation urls..
        """

        for url in self.extra_endpoints:
            response = self.client.get('/{}'.format(url))
            self.valid_html_response(url, response)

    def test_aggregation_wegdelenendpoint(self):

        url = 'predictiveparking/metingen/aggregations/wegdelen/?format=json'
        params = '&date_gte=2016&hour_gte=0&hour_lte=23'
        dayrange = '&day_lte=6&day_gte=0'
        response = self.client.get('/{}'.format(url+params+dayrange))
        for _wegdeelid, data in response.data['wegdelen'].items():
            # self.assertIn('bgt_functie', data)
            self.assertIn('total_vakken', data)
            # self.assertIn('fiscaal', data)
            self.assertIn('unique_scans', data)
            self.assertIn('days_seen', data)
            self.assertIn('occupation', data)

        self.assertIn('selection', response.data)

    def test_aggregation_wegdelenendpoint_explain(self):

        url = 'predictiveparking/metingen/aggregations/wegdelen/?format=json'
        params = '&date_gte=2016&hour_gte=0&hour_lte=23'
        dayrange = '&day_lte=6&day_gte=0'

        response = self.client.get(
            '/{}'.format(url+params+dayrange+'&explain'))

        for _wegdeelid, data in response.data['wegdelen'].items():
            # self.assertIn('bgt_functie', data)
            self.assertIn('total_vakken', data)
            # self.assertIn('fiscaal', data)
            self.assertIn('unique_scans', data)
            self.assertIn('days_seen', data)
            self.assertIn('occupation', data)
            self.assertIn('cardinal_vakken_by_day', data)

        self.assertIn('selection', response.data)

    def test_aggregation_wegdelenendpoint_filter_no_result(self):

        url = 'predictiveparking/metingen/aggregations/wegdelen/?format=json'
        params = '&date_lte=2016&hour_gte=0&hour_lte=23'
        dayrange = '&day_lte=6&day_gte=0'
        response = self.client.get('/{}'.format(url+params+dayrange))
        self.assertEqual(len(response.data['wegdelen']), 0)

    def test_selection_range(self):

        url = 'predictiveparking/metingen/aggregations/wegdelen/?format=json'

        range_fields = ['day', 'minute', 'hour', 'month']

        for field in range_fields:
            params = f'&{field}_lte=6&{field}_gte=0'
            response = self.client.get('/{}'.format(url+params))
            self.assertIn(f'{field}_gte', response.data['selection'])
            self.assertIn(f'{field}_lte', response.data['selection'])
            self.assertNotIn(f'{field}', response.data['selection'])

            response2 = self.client.get('/{}'.format(url + f'&{field}=1'))
            self.assertNotIn(f'{field}_lte', response2.data['selection'])
            self.assertNotIn(f'{field}_gte', response2.data['selection'])
            self.assertIn(f'{field}', response2.data['selection'])

    def test_aggregation_vakken(self):

        url = 'predictiveparking/metingen/aggregations/vakken/?format=json'
        response = self.client.get('/{}'.format(url))
        self.assertIn('vakken', response.data)
        self.assertIn('scancount', response.data)
