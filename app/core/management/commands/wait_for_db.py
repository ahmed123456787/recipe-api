"""
django command to wait for database to be availabel
"""
import time
from psycopg2 import OperationalError as psyerr
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        self.stdout.write("waiting for databse.....")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except [psyerr, OperationalError]:
                self.stdout.write("database is unvailable")   
                time.sleep(1)
                
        self.stdout.write(self.style.SUCCESS("dataabse available"))         