import logging
# import json

from unittest import skip

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from . import factories

LOG = logging.getLogger(__name__)


class MetingenTestCase(APITestCase):
    """
    Test some metingen
    """

    def setUp(self):
        """
        Create 100 test items
        """

        for _i in range(100):
            factories.ScanFactory.create()

    @skip('no individual scans in api please.')
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

    @skip('no individual scans in api please.')
    def test_metingen(self):

        scan_url = reverse('scan-list')
        response = self.client.get(scan_url)

        self.valid_response(scan_url, response)
        self.assertEqual(response.data['count'], 100)
        self.assertNotEqual(response.data['count'], 101)
