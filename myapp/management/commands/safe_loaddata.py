from django.core.management.base import BaseCommand
from django.core.management import call_command
from myapp.models import Product, UserProfile


class Command(BaseCommand):
    help = 'Safely loads datadump.json only if database is empty'

    def handle(self, *args, **kwargs):
        if Product.objects.count() == 0:
            self.stdout.write('Database is empty. Preparing to load data...')
            UserProfile.objects.all().delete()
            self.stdout.write('Cleared auto-created profiles. Loading fixture...')
            call_command('loaddata', 'datadump.json')
            self.stdout.write('Data loaded successfully!')
        else:
            self.stdout.write('Database already has data. Skipping loaddata.')
