import logging
import json

# Packages
from rest_framework.test import APITestCase
# from rest_framework.reverse import reverse
# Project
from metingen.tests import factories as scan_factories

# from wegdelen.tests import factories as bgt_factories


LOG = logging.getLogger(__name__)


def pretty_data(data):
    return json.dumps(data, indent=4, sort_keys=True)


class BrowseDatasetsTestCase(APITestCase):
    """
    Verifies that browsing the API works correctly.
    """

    datasets = [
        'predictiveparking/metingen/scans',
        'predcitiveparking/wegdelen',
        'predcitiveparking/vakken',
    ]

    extra_endpoitns = [
        'predictiveparking/voutevakken',
        'predictiveparking/gratis',
    ]

    def setUp(self):
        """
        This create a graph of objects that point to
        each others with nice working links

        This is done to test the generated
        links.
        """

        for _i in range(5):
            scan_factories.ScanFactory.create()

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

    def test_details_html(self):
        for url in self.datasets:
            response = self.client.get('/{}/?format=api'.format(url))

            url = response.data['results'][0]['_links']['self']['href']
            detail = self.client.get(url)

            self.valid_html_response(url, detail)

            # self.assertIn('_display', detail.data)
