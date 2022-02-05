import time

from django.core.management.base import BaseCommand

from parsers.loader import load


class Command(BaseCommand):
    help = 'Run loader'

    def handle(self, *args, **options):

        start = time.time()

        errors = load()

        end = time.time()
        t = end - start

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded in '
                                             f'{int(t // 60 // 60 % 60)} : {int(t // 60 % 60)} : {int(t % 60)}'))
        self.stdout.write(f'With following errs:\n {str(errors)}')
