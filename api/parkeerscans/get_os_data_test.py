import os
import unittest
from unittest.mock import patch
from collections import defaultdict

from swiftclient.client import Connection
from swiftclient.exceptions import ClientException

from get_os_data import parkeren_conn, StoreObjectStorage


valid_json_result = ({}, b'{"files": ["bar", "etc", "foo"]}')
invalid_json_result = ({}, b'{"files": ["bar", "etc", "foo",]}')


class TestHandledFiles(unittest.TestCase):

    def tearDown(self):

        # ensure environment variables are removed
        environment_vars_used = [
            'HANDLED_FILES_ENV_TEST',
            'datapunt_import_status/HANDLED_FILES_ENV_TEST'
        ]
        for item in environment_vars_used:
            if item in os.environ:
                del os.environ[item]

    @patch.object(Connection, 'get_object', return_value=valid_json_result)
    def test_load_handled_files_valid_json(self, _):
        store = StoreObjectStorage('handled_files_test', container_name='foobar', connection=Connection())
        store.whitelisted.append('foobar')

        items = store.load_handled_files()
        self.assertEqual(items, {'foo', 'bar', 'etc'})

    @patch.object(Connection, 'get_object', return_value=invalid_json_result)
    def test_load_handled_files_invalid(self, _):
        store = StoreObjectStorage('handled_files_test', container_name='foobar', connection=Connection())
        store.whitelisted.append('foobar')

        items = store.load_handled_files()
        self.assertEqual(items, set())

    def test_load_handled_files_no_connection(self):
        store = StoreObjectStorage(
            filename='handled_files',
            container_name='foobar',
            connection=MockedConnection(unable_to_connect=True)
        )
        store.whitelisted.append('foobar')

        file_names = ['foo', 'bar', 'etc']

        # How to handle load and save during connection errors, do we fail and continue
        store.save_handled_files(file_names)
        store.whitelisted.append('foobar')

        # items should be empty since there is no internet connection
        items = store.load_handled_files()
        self.assertEqual(items, set())

    def test_save_handled_files(self):
        store = StoreObjectStorage(
            filename='handled_files_test',
            container_name='foobar',
            connection=MockedConnection()
        )
        store.whitelisted.append('foobar')

        file_names = ['foo', 'bar', 'etc']

        store.save_handled_files(file_names)
        store.whitelisted.append('foobar')
        items = store.load_handled_files()
        self.assertEqual(items, {'foo', 'bar', 'etc'})

    def test_save_handled_files_overwrite(self):
        store = StoreObjectStorage(
            filename='handled_files_test',
            container_name='foobar',
            connection=MockedConnection()
        )
        store.whitelisted.append('foobar')

        file_names = ['foo', 'bar', 'etc']

        items = store.load_handled_files()
        self.assertEqual(items, set([]))

        store.save_handled_files(file_names)
        items = store.load_handled_files()

        self.assertEqual(items, {'foo', 'bar', 'etc'})

        items = store.load_handled_files(filename="foo")
        self.assertEqual(items, set([]))

        store.save_handled_files(file_names, filename="foo")
        items = store.load_handled_files(filename="foo")
        self.assertEqual(items, {'foo', 'bar', 'etc'})

        file_names = ['etc', 'def']
        store.save_handled_files(file_names, filename="foo")
        items = store.load_handled_files(filename="foo")
        self.assertEqual(items, {'foo', 'bar', 'etc', 'def'})

    @unittest.skip
    def test_save_load_overwrite_to_prod_object_store(self):
        """Warning this test will connect with the production object store"""
        store = StoreObjectStorage(filename='handled_files_test', container_name='datapunt_import_status/test', connection=parkeren_conn)

        file_names = ['foo', 'bar', 'etc']

        store.save_handled_files(file_names)

        items = store.load_handled_files()
        self.assertEqual(items, {'foo', 'bar', 'etc'})

        file_names = ['def']
        store.save_handled_files(file_names)

        items = store.load_handled_files()
        self.assertEqual(items, {'foo', 'bar', 'etc', 'def'})

        # empty the file after the test
        store.save('')
        items = store.load_handled_files()
        self.assertEqual(items, set())


class MockedConnection:
    def __init__(self, unable_to_find_file=False, unable_to_connect=False):
        self.store = defaultdict(dict)
        self.unable_to_find_file = unable_to_find_file
        self.unable_to_connect = unable_to_connect

    def get_object(self, container_name, filename):
        if self.unable_to_connect:
            raise ClientException("Mocked unable to connect")
        try:
            return self.store[container_name][filename]
        except KeyError:
            raise ClientException('Mocked')

    def put_object(self, container_name, filename, data):
        if self.unable_to_connect:
            raise ClientException("Mocked unable to connect")

        if self.unable_to_find_file:
            raise ClientException("Mocked resource could not be found")

        self.store[container_name].setdefault(filename, {})
        self.store[container_name][filename] = ({}, bytes(data, 'utf-8'))


if __name__ == '__main__':
    unittest.main()

