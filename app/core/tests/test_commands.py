from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTest(TestCase):

    @patch('django.db.utils.ConnectionHandler.__getitem__',
           return_value=True)
    def test_if_db_ready(self, gi):
        '''
        Tests if wait_for_db calls database one time
        if the connection with the database is successful
        '''
        call_command('wait_for_db')
        self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_db_not_ready(self, ts):
        '''
        Tests if wait_for_db is called multiple time
        when the connection with database if failed
        '''
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
