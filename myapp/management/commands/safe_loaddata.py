from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from myapp.models import Product, UserProfile, create_user_profile


class Command(BaseCommand):
    help = 'Safely loads datadump.json only if database is empty'

    def handle(self, *args, **kwargs):
        self.stdout.write('Disconnecting post_save signal...')
        post_save.disconnect(create_user_profile, sender=User)

        self.stdout.write('Clearing conflicting data...')
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Product.objects.all().delete()

        self.stdout.write('Loading fixture...')
        call_command('loaddata', 'datadump.json')

        self.stdout.write('Reconnecting post_save signal...')
        post_save.connect(create_user_profile, sender=User)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
