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
    We test elastic and database API
    We load some custom datasets in elastic using
    logstash. We cannot use the 'default' way
    to create test data..
    """

    datasets = [
        # 'parkeerscans/metingen/scans',
        'parkeerscans/wegdelen',
        'parkeerscans/vakken',
    ]

    extra_endpoints = [
        'parkeerscans/voutevakken',
        'parkeerscans/voutevakken?buurt=W12b&aantal=2',
        'parkeerscans/gratis',
        'parkeerscans/gratis?type=all',
    ]

    @classmethod
    def setUpClass(cls):
        """
        This django app is merely a viewer on data
        we load testdata into database using special created
        test data around the silodam area.

        NOTE TEST ELASTIC MUST BE PREPARED

        read docker-test.sh
        """
        # we load some external testdata
        bash_command = "bash testdata/loadtestdata.sh"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)

        output, _error = process.communicate()

        log.debug(output)

        db.connections.close_all()

        log.debug(
            'Wegdelen loaded: %d',
            WegDeel.objects.count())

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
        url = '/parkeerscans/?format=api'
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

        url = 'parkeerscans/metingen/aggregations/wegdelen/?format=json'
        params = '&year_gte=2016&hour_gte=0&hour_lte=23'
        dayrange = '&day_lte=6&day_gte=0'
        response = self.client.get('/{}'.format(url+params+dayrange))

        for _wegdeelid, data in response.data['wegdelen'].items():
            # self.assertIn('bgt_functie', data)
            self.assertIn('unique_scans', data)
            self.assertIn('days_seen', data)
            # self.assertIn('fiscaal', data)
            if data.get('total_vakken'):
                self.assertIn('total_vakken', data)
                self.assertIn('avg_occupancy', data)

        self.assertIn('selection', response.data)

    def test_aggregation_wegdelenendpoint_explain(self):

        url = 'parkeerscans/metingen/aggregations/wegdelen/?format=json'
        params = ''
        dayrange = '&day_lte=6&day_gte=0'

        response = self.client.get(
            '/{}'.format(url+params+dayrange+'&explain'))

        for _wegdeelid, data in response.data['wegdelen'].items():
            # self.assertIn('bgt_functie', data)
            self.assertIn('unique_scans', data)
            self.assertIn('days_seen', data)
            if data.get('total_vakken'):
                self.assertIn('total_vakken', data)
                self.assertIn('avg_occupancy', data)
                self.assertIn('cardinal_vakken_by_day', data)

        self.assertIn('selection', response.data)
        selection = response.data['selection']
        self.assertIn('day_lte', selection)
        self.assertNotIn('day', selection)
        self.assertIn('day_gte', selection)
        self.assertIn('hour_lte', selection)
        self.assertIn('hour_gte', selection)

    def test_aggregation_wegdelenendpoint_filter_no_result(self):

        url = 'parkeerscans/metingen/aggregations/wegdelen/?format=json'
        params = '&year=2015'
        dayrange = '&day_lte=6&day_gte=0'
        response = self.client.get('/{}'.format(url+params+dayrange))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['wegdelen']), 0)

    def test_selection_range(self):

        url = 'parkeerscans/metingen/aggregations/wegdelen/?format=json'

        # TODO auth for minute field
        # range_fields = ['minute', 'hour', 'month']

        range_fields = [
            # range  gte, lte, answers
            ('hour',  (0, 6), (0, 6)),
            ('month',  (0, 6), ("january  ", "july     ")),
        ]

        for field, r, a in range_fields:

            # do request with range
            params = f'&{field}_lte={r[1]}&{field}_gte={r[0]}'
            response = self.client.get('/{}'.format(url+params))
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'{field}_gte', response.data['selection'])
            self.assertIn(f'{field}_lte', response.data['selection'])
            self.assertNotIn(f'{field}', response.data['selection'])

            self.assertEqual(response.data['selection'][f'{field}_gte'], a[0])
            self.assertEqual(response.data['selection'][f'{field}_lte'], a[1])

            # request with no range
            response2 = self.client.get('/{}'.format(url + f'&{field}=1'))
            self.assertNotIn(f'{field}_lte', response2.data['selection'])
            self.assertNotIn(f'{field}_gte', response2.data['selection'])
            self.assertIn(f'{field}', response2.data['selection'])

    def test_day_selection(self):
        test_selections = [
            (0, 0, 200),
            (2, 0, 200),
            (0, 2, 200),
        ]
        url = 'parkeerscans/metingen/aggregations/wegdelen/?format=json'
        for low, high, status in test_selections:

            params = f'&day_lte={high}&day_gte={low}'
            response = self.client.get('/{}'.format(url+params))
            self.assertEqual(response.status_code, status)

            if status == 200:
                self.assertNotIn('day', response.data['selection'])

    def test_bbox(self):

        test_data_params = '&year_lte=2016&hour_gte=0&hour_lte=23'

        bbox_urls = [
            '/parkeerscans/metingen/aggregations/wegdelen/?format=json' +
            test_data_params,
            '/parkeerscans/metingen/aggregations/vakken/?format=json'
        ]

        lat1 = '52.37560'
        lat2 = '52.39969'

        lon1 = '4.68565'
        lon2 = '5.29360'

        latfail = '809.38560'
        lonfail = '809.38560'

        bbox = [lon1, lat1, lon2, lat2]

        valid_bbox = ",".join(bbox)
        # wrong order
        invalid_bbox = ",".join([latfail, lonfail, lon1, latfail])

        for url in bbox_urls:
            params = f'&bbox={valid_bbox}'
            response = self.client.get(url+params)
            self.assertEqual(response.status_code, 200)

            params = f'&bbox={invalid_bbox}'
            response = self.client.get(url+params)
            self.assertEqual(response.status_code, 400)

    def test_stadsdeel(self):
        url = '/parkeerscans/metingen/aggregations/wegdelen/?format=json'

        test_params = '&stadsdeel=A'

        response = self.client.get(url+test_params)
        self.assertEqual(response.status_code, 200)
        selection = response.data['selection']

        self.assertIn('stadsdeel', selection)
        self.assertEqual('A', selection['stadsdeel'])

        # stadsdeel does not exist
        test_params = '&stadsdeel=X'
        response = self.client.get(url+test_params)
        self.assertEqual(response.status_code, 400, 'stadsdeel?')
        self.assertNotIn('selection', response.data)

    def test_term_filters(self):
        """
        see if all terms parameters get into selection
        """
        terms = {
            'stadsdeel': 'A',
            'buurtcode': 'Aco',
            'buurtcombinatie': 'Aco1',
            'bgt_wegdeel': 'idx',
            'day': (0, 'monday   '),
            'year': 2017,
            'hour': 1,
            'month': (10, 'november '),
            # 'minute': 1,
            'qualcode': 'test',
            'sperscode': 'test',
        }

        url = '/parkeerscans/metingen/aggregations/wegdelen/?format=json'

        for term_field, test_value in terms.items():
            outcome = test_value
            if isinstance(test_value, tuple):
                test_value, outcome = test_value
            test_params = f'&{term_field}={test_value}'
            response = self.client.get(url+test_params)
            self.assertEqual(response.status_code, 200)
            selection = response.data['selection']
            self.assertIn(term_field, selection)
            self.assertEqual(outcome, selection[term_field])

    def test_year_field(self):
        """
        Test date field cleanup and presence
        """

        test_date_params = '&year_lte=2024&year_gte=2015'
        url = '/parkeerscans/metingen/aggregations/wegdelen/?format=json'

        response = self.client.get(url+test_date_params)
        selection = response.data['selection']

        self.assertIn('year_lte', selection)
        self.assertIn('year_gte', selection)
        self.assertEqual(2024, selection['year_lte'])
        self.assertEqual(2015, selection['year_gte'])

    def test_aggregation_vakken(self):

        url = 'parkeerscans/metingen/aggregations/vakken/?format=json'
        response = self.client.get('/{}'.format(url))
        self.assertEqual(response.status_code, 200)
        self.assertIn('vakken', response.data)
        self.assertIn('scancount', response.data)
