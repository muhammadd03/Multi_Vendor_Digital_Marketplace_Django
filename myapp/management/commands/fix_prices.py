from django.core.management.base import BaseCommand
from myapp.models import Product


class Command(BaseCommand):
    help = 'Fix confirmed product prices from the presentation'

    def handle(self, *args, **kwargs):
        updates = [
            ('keychain', 450),
            ('gajray',   1000),
            ('care bear', 1800),
            ('tote',     1200),
        ]
        for keyword, price in updates:
            updated = (
                Product.objects
                       .filter(name__icontains=keyword)
                       .exclude(name__icontains='pearl')
                       .update(price=price)
            )
            self.stdout.write(f"Updated {updated} product(s) matching '{keyword}' → PKR {price:,}")
        self.stdout.write(self.style.SUCCESS('✦ Prices fixed.'))
