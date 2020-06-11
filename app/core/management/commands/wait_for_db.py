import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Waiting for the database...')
        db_catch = False
        while not db_catch:
            try:
                db_catch = connections['default']
            except OperationalError:
                self.stderr.write(
                    'The database is unavailable, trying one more time...'
                )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is ready'))
