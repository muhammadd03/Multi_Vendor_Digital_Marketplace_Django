from django.core.management.base import BaseCommand
from myapp.models import Product
import os


class Command(BaseCommand):
    help = 'Check image paths and existence for all products'

    def handle(self, *args, **kwargs):
        for p in Product.objects.all():
            path = p.image.path if p.image else 'NO IMAGE'
            exists = os.path.exists(p.image.path) if p.image else False
            self.stdout.write(f'{p.name}: {path} | EXISTS: {exists}')
