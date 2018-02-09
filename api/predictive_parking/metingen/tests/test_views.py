import logging
# import json

from unittest import skip

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

from . import factories
from .. import queries

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

    def test_month_range(self):
        """
        test range functions
        """
        # start , end , expected
        tests = [
            [1, 4,  [1, 2, 3, 4]],  # feb-may
            [11, 2, [11, 0, 1, 2]],  # dec-march
            [8, 0, [8, 9, 10, 11, 0]],  # sept-jan
            [0, 0, [0]],
            [1, 1, [1]],
            [11, 11, [11]],
        ]

        for start, end, expected in tests:

            cleaned_data = {
                'month_gte': start,
                'month_lte': end,
                'month': 'should be removed'
            }

            should_query = queries.make_field_bool_query(
                'month', 'month_gte', 'month_lte',
                cleaned_data, queries.MONTHS)

            self.assertEqual(
                len(should_query['bool']['should']), len(expected),
                should_query['bool']['should'])

            options = queries.find_options(start, end, 12)
            self.assertEqual(set(options), set(expected))

            self.assertNotIn('month', cleaned_data)

    def test_term_options(self):

        test_params = {
            'week': 44,
            'hour': 12,
            'month': 4,
        }

        cleaned, err = queries.clean_parameter_data(test_params)
        self.assertEqual(err, None, err)

        cleaned, err = queries.clean_parameter_data({'hour': 60})
        self.assertNotEqual(err, None, err)
        cleaned, err = queries.clean_parameter_data({'minute': 60})
        self.assertNotEqual(err, None, err)
        cleaned, err = queries.clean_parameter_data({'month': 12})
        self.assertNotEqual(err, None, err)
