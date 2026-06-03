import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Product, OrderDetail, Review


class Command(BaseCommand):
    help = 'Seed the database with Yarnivore sample products, orders, and reviews'

    def handle(self, *args, **kwargs):
        # ── 4a: Clear existing products ──────────────────────────────────────
        deleted, _ = Product.objects.all().delete()
        self.stdout.write(f'Deleted {deleted} existing products.')

        # ── 4b: Find vendor user ─────────────────────────────────────────────
        vendor_user = User.objects.filter(profile__is_vendor=True).first()
        if not vendor_user:
            self.stdout.write(self.style.ERROR(
                'No vendor found. Please create a vendor account first via /auth/ then mark it as vendor in admin.'
            ))
            return
        self.stdout.write(f'Using vendor: {vendor_user.username}')

        # ── 4c: Create 8 products ─────────────────────────────────────────────
        products_data = [
            {
                "name": "Care Bear",
                "description": (
                    "Bring a whole lot of comfort into your life with this adorable, handmade green bear! "
                    "Stitched with love and care, this soft plushie features a beautifully detailed flower "
                    "right on its belly. Whether you are looking for the perfect nursery decoration, a "
                    "nostalgic gift for a loved one, or a cozy companion for yourself, this little bear "
                    "is guaranteed to bring smiles and good vibes.\n\nKey Features:\n"
                    "- 100% handmade with premium, soft yarn\n"
                    "- Features a detailed, stitched four-leaf clover emblem\n"
                    "- Perfect gift for birthdays and baby showers"
                ),
                "price": 1800,
                "image": "products/care_bear.png",
            },
            {
                "name": "Gajray",
                "description": (
                    "Celebrate tradition with a modern, everlasting twist. These beautiful handmade crochet "
                    "gajray feature intricately stitched velvet-style red roses nested in a soft cream-white "
                    "border. Perfect for weddings, mehndi functions, Eid, or festive celebrations, these "
                    "floral wrist cuffs give you the classic, elegant look of fresh flowers without ever "
                    "wilting or fading.\n\nKey Features:\n"
                    "- 100% handmade with premium, ultra-soft yarn\n"
                    "- Features a stunning textured bouquet design of miniature red roses\n"
                    "- Durable and reusable\n"
                    "- Comfortable stretchable fit"
                ),
                "price": 1000,
                "image": "products/gajray_red.png",
            },
            {
                "name": "Royal Pearl & Crochet Rose Wristlet",
                "description": (
                    "Add a touch of timeless royalty to your festive attire. This exquisite gajra pairs a "
                    "beautifully hand-stitched, deep crimson crochet rose with a stunning double strand of "
                    "elegant faux pearls. Designed to slide comfortably onto your wrist, it offers a "
                    "sophisticated, regal flair for brides, bridesmaids, or festive guests. The ultimate "
                    "heirloom accessory you can cherish forever.\n\nKey Features:\n"
                    "- Meticulously layered hand-crocheted red rose\n"
                    "- High-shine flexible pearl bead elastic band\n"
                    "- Perfect sustainable alternative to fresh flower gajray"
                ),
                "price": 1200,
                "image": "products/gajray_pearl.png",
            },
            {
                "name": "Sunflower Square Tote",
                "description": (
                    "Carry a pocketful of sunshine wherever you go! This gorgeous boho-chic tote bag is "
                    "meticulously crafted from sage green squares, each showcasing a vibrant, blooming "
                    "sunflower. Complete with a secure wooden button closure and durable, comfortable "
                    "shoulder straps, this tote is as functional as it is stylish. The ultimate accessory "
                    "for market runs, beach days, or casual weekend outings.\n\nKey Features:\n"
                    "- Classic vintage square design\n"
                    "- Spacious enough for daily essentials\n"
                    "- Wooden button closure"
                ),
                "price": 2500,
                "image": "products/tote_sunflower.png",
            },
            {
                "name": "Retro Daisy Patchwork Cardigan",
                "description": (
                    "Wrap yourself in cozy, nostalgic charm with this beautifully handcrafted daisy "
                    "cardigan. Made from individual patchwork squares, this chunky knit features stunning, "
                    "raised daisies set against a soft, dusty blue-gray background. With its relaxed, "
                    "slightly cropped silhouette, drop shoulders, and classic ribbed cuffs, it is the "
                    "ultimate statement piece for layering.\n\nKey Features:\n"
                    "- 100% meticulously hand-knitted with premium soft-blend yarn\n"
                    "- Features eye-catching textured 3D daisy squares\n"
                    "- Comfy oversized fit with cozy ribbed cuffs"
                ),
                "price": 4500,
                "image": "products/cardigan_daisy.png",
            },
            {
                "name": "Bloom & Go Flower Keychains",
                "description": (
                    "Brighten up your keys, backpack, or purse with these cheerful, pocket-sized floral "
                    "keychains. Choose between a sunny, radiant sunflower or a classic, crisp white daisy "
                    "— both complete with a cute little green leaf accent. Light, durable, and bursting "
                    "with personality, these little blooms ensure you will never lose track of your keys "
                    "again.\n\nKey Features:\n"
                    "- Available in Sunflower and Daisy designs\n"
                    "- Includes a sturdy silver-tone key ring and chain\n"
                    "- A wonderful affordable gift"
                ),
                "price": 450,
                "image": "products/keychain_bloom.png",
            },
            {
                "name": "Blooming Crochet Sunflower Bouquet",
                "description": (
                    "Give a gift that never wilts! This stunning single-stem crochet sunflower is "
                    "beautifully crafted with bright yellow petals, detailed leaves, and a textured center. "
                    "It comes pre-wrapped in premium aesthetic green paper and tied with a vibrant satin "
                    "yellow ribbon, ready to be gifted directly to someone special. Perfect for "
                    "graduations, anniversaries, or just to brighten someone's day permanently.\n\nKey Features:\n"
                    "- Handcrafted everlasting flower\n"
                    "- Beautifully gift-wrapped with a matching satin bow\n"
                    "- Thoughtful sustainable alternative to fresh flowers"
                ),
                "price": 1500,
                "image": "products/bouquet_sunflower.png",
            },
        ]

        products = []
        for p in products_data:
            product = Product.objects.create(
                seller=vendor_user,
                name=p['name'],
                description=p['description'],
                price=p['price'],
                image=p['image'],
            )
            products.append(product)
            self.stdout.write(f'  Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products.'))

        # ── 4d: Create 10 dummy orders ────────────────────────────────────────
        customer_users = User.objects.filter(profile__is_vendor=False)
        names = [
            "Ayesha Khan", "Sara Ahmed", "Hira Malik", "Zara Siddiqui", "Maryam Raza",
            "Fatima Noor", "Sana Tariq", "Nadia Hassan", "Rabia Sheikh", "Amna Javed",
        ]
        phones = [
            "0312-1234567", "0333-9876543", "0321-4567890", "0345-1122334", "0311-9988776",
            "0322-5544332", "0301-6677889", "0313-4433221", "0341-7788990", "0351-2233445",
        ]
        addresses = [
            "House 12, Block B, North Nazimabad, Karachi",
            "Flat 5, Gulshan-e-Iqbal Block 13, Karachi",
            "Plot 44, DHA Phase 2, Karachi",
            "House 7, Clifton Block 4, Karachi",
            "Apartment 3B, Gulberg, Karachi",
            "House 99, PECHS Block 6, Karachi",
            "Flat 2, Nazimabad No. 2, Karachi",
            "House 18, Bahadurabad, Karachi",
            "Plot 67, Korangi Industrial Area, Karachi",
            "House 31, FB Area Block 16, Karachi",
        ]

        for i in range(10):
            product = products[i % len(products)]
            customer = customer_users[i % len(customer_users)] if customer_users.exists() else vendor_user
            OrderDetail.objects.create(
                customer_email=f"customer{i + 1}@example.com",
                product=product,
                amount=int(product.price),
                has_paid=True,
                full_name=names[i],
                phone_number=phones[i],
                address=addresses[i],
                city="Karachi",
                payment_method=random.choice(['bank_transfer', 'cod']),
            )
            product.total_sales += 1
            product.total_sales_amount += int(product.price)
            product.save()

        self.stdout.write(self.style.SUCCESS('Created 10 dummy orders.'))

        # ── 4e: Create dummy reviews ─────────────────────────────────────────
        review_data = [
            ("Absolutely love it! The quality is amazing, so soft and cute.", 5),
            ("Perfect gift for my friend's birthday. She was thrilled!", 5),
            ("Beautiful craftsmanship. Looks even better in person.", 4),
            ("Very well made, exactly as described. Will order again!", 5),
            ("Lovely product, fast delivery. Highly recommend.", 4),
            ("Such a unique and thoughtful gift. Really impressed.", 5),
            ("Great quality for the price. Will definitely reorder.", 4),
            ("The packaging was so aesthetic too. Loved the whole experience.", 5),
            ("Super cute and durable. Worth every rupee.", 5),
            ("Ordered as a wedding gift and everyone loved it!", 5),
        ]

        review_count = 0
        for i, product in enumerate(products):
            for j in range(2):
                idx = (i * 2 + j) % len(review_data)
                comment, rating = review_data[idx]
                _, created = Review.objects.get_or_create(
                    product=product,
                    customer=vendor_user,
                    defaults={'rating': rating, 'comment': comment},
                )
                if created:
                    review_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {review_count} reviews.'))
        self.stdout.write(self.style.SUCCESS('✦ Seed complete!'))
