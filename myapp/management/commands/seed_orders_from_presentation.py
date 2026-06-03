from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import F
from django.utils import timezone
from myapp.models import Product, OrderDetail


class Command(BaseCommand):
    help = 'Seed 10 presentation orders, replacing all existing orders'

    def handle(self, *args, **kwargs):
        # ── Delete existing orders ────────────────────────────────────────────
        deleted, _ = OrderDetail.objects.all().delete()
        self.stdout.write(f'Deleted {deleted} existing orders.')

        # Reset product sales counters so they don't double-count
        Product.objects.all().update(total_sales=0, total_sales_amount=0)

        # ── Resolve vendor ────────────────────────────────────────────────────
        vendor = User.objects.filter(profile__is_vendor=True).first()
        if not vendor:
            self.stdout.write(self.style.ERROR('No vendor with is_vendor=True found.'))
            return

        # ── Resolve the 4 product types ───────────────────────────────────────
        keychain = (
            Product.objects.filter(name__icontains='keychain').first()
            or Product.objects.filter(name__icontains='Bloom & Go').first()
        )
        mini_bag = Product.objects.filter(name__icontains='tote').first()
        stuffed  = Product.objects.filter(name__icontains='care bear').first()
        gajray   = (
            Product.objects.filter(name__icontains='gajray')
                           .exclude(name__icontains='pearl')
                           .first()
        )

        missing = [
            name for name, obj in [
                ('Keychain / Charm', keychain),
                ('Mini Bag / Tote',  mini_bag),
                ('Care Bear',        stuffed),
                ('Gajray',           gajray),
            ] if obj is None
        ]
        if missing:
            self.stdout.write(self.style.ERROR(f'Could not find products: {missing}'))
            return

        self.stdout.write(f'  Keychain → {keychain.name}  (Rs. {keychain.price})')
        self.stdout.write(f'  Tote     → {mini_bag.name}  (Rs. {mini_bag.price})')
        self.stdout.write(f'  Stuffed  → {stuffed.name}  (Rs. {stuffed.price})')
        self.stdout.write(f'  Gajray   → {gajray.name}  (Rs. {gajray.price})')

        # ── 10-order sequence from the presentation ───────────────────────────
        product_sequence = [
            keychain,   # 1
            mini_bag,   # 2
            stuffed,    # 3
            gajray,     # 4
            keychain,   # 5
            mini_bag,   # 6
            stuffed,    # 7
            mini_bag,   # 8
            gajray,     # 9
            keychain,   # 10
        ]

        # ── Create orders ─────────────────────────────────────────────────────
        for i, product in enumerate(product_sequence):
            order = OrderDetail.objects.create(
                customer_email=f'seed_customer{i + 1}@example.com',
                product=product,
                amount=int(product.price),
                has_paid=True,
                payment_method='cod',
                full_name=f'Seed Customer {i + 1}',
                phone_number=f'03{i + 1}1-234567',
                address=f'Sample Address {i + 1}, Karachi',
                city='Karachi',
            )
            # auto_now_add blocks created_on in create(); set it via update()
            backdated = timezone.now() - timezone.timedelta(days=(10 - i))
            OrderDetail.objects.filter(pk=order.pk).update(created_on=backdated)

            # Update product counters using F() to avoid race conditions
            Product.objects.filter(pk=product.pk).update(
                total_sales=F('total_sales') + 1,
                total_sales_amount=F('total_sales_amount') + int(product.price),
            )

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write('Orders created:')
        counts = {}
        for p in product_sequence:
            counts[p.name] = counts.get(p.name, 0) + 1
        for name, count in sorted(counts.items(), key=lambda x: -x[1]):
            self.stdout.write(f'  {count}x  {name}')

        self.stdout.write(self.style.SUCCESS(f'\n✦ Done — {len(product_sequence)} orders created.'))
