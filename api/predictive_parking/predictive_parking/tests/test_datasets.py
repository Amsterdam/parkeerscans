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
        This create a graph of objects that point to
        each others with nice working links

        This is done to test the generated
        links.
        """
        # we load some external testdata
        bash_command = "bash testdata/loadtestdata.sh"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)

        output, _error = process.communicate()

        bash_command = "bash testdata/loadelastic.sh"
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
