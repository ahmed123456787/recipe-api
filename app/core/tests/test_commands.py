"""
Custom amngement commands .
"""

from unittest.mock import patch
from psycopg2 import OperationalError as psyerr
from django.core.management import call_command
from django.test import SimpleTestCase
from django.db.utils import OperationalError

# @patch("core.management.commands.wait_for_db")
# class CommandTest(SimpleTestCase):
    
#     def test_wait_db(self,patched_check):
#         """test waiting for database if database ready"""
#         patched_check.return_value = True
        
#         call_command('wait_for_db')
#         patched_check.assert_called_once_with(databases=['default'])
    
#     def test_wait_for_db_delay (self,patched_check):
#         """test waitnig for databse when getting opertionalerror"""
#         patched_check.side_effect = [psyerr] *2 \
#             [OperationalError] * 3 + [True]    
        
        