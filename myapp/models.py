from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    file = models.FileField(upload_to='uploads', blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    total_sales_amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class OrderDetail(models.Model):
    customer_email = models.EmailField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
    has_paid = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    reciept = models.ImageField(null=True, blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[('bank_transfer', 'Bank Transfer'), ('cod', 'Cash on Delivery')],
        default='bank_transfer'
    )


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Vendor' if self.is_vendor else 'Customer'}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'customer')

    def __str__(self):
        return f"{self.customer.username} - {self.product.name} ({self.rating}★)"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
