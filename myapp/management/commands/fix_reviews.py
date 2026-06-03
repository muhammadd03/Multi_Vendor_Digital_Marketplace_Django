from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Product, Review


REVIEW_MAP = [
    ('care bear', 'zara',   5, "The softest, most adorable thing I've ever seen. Perfect gift!"),
    ('gajray',    'ayesha', 5, "Wore it to my cousin's mehndi and got so many compliments. Absolutely love it!"),
    ('pearl',     'maryam', 5, "Looked so elegant on my wrist. Everyone asked where I got it from!"),
    ('tote',      'hira',   4, "Super cute and spacious. The sunflower design is gorgeous."),
    ('cardigan',  'sana',   5, "Literally the coziest thing I own. The daisies are so detailed!"),
    ('bloom',     'nadia',  5, "Bought two as gifts. Both friends loved them. Great quality!"),
    ('bouquet',   'fatima', 5, "Gifted this at a graduation. Everyone thought it was real at first!"),
]


class Command(BaseCommand):
    help = 'Replace all reviews with one authentic review per product'

    def handle(self, *args, **kwargs):
        deleted, _ = Review.objects.all().delete()
        self.stdout.write(f'Deleted {deleted} existing reviews.')

        created_count = 0
        for keyword, username, rating, comment in REVIEW_MAP:
            # Find the product — gajray must exclude pearl wristlet
            qs = Product.objects.filter(name__icontains=keyword)
            if keyword == 'gajray':
                qs = qs.exclude(name__icontains='pearl')

            product = qs.first()
            if not product:
                self.stdout.write(self.style.WARNING(f'  No product found for keyword "{keyword}" — skipping.'))
                continue

            reviewer, _ = User.objects.get_or_create(username=username)

            Review.objects.create(
                product=product,
                customer=reviewer,
                rating=rating,
                comment=comment,
            )
            created_count += 1
            self.stdout.write(f'  {rating}★  {reviewer.username} → {product.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✦ Done — {created_count} reviews created.'))
