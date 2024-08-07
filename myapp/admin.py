from django.contrib import admin
from .models import Product,OrderDetail
# from .custom_admin import custom_admin_site

# class OrderDetailAdmin(admin.ModelAdmin):
#     list_display = ['id', 'customer_email', 'product', 'amount', 'has_paid', 'created_on']
#     actions = ['mark_as_paid']

#     def mark_as_paid(self, request, queryset):
#         queryset.update(has_paid=True)
#     mark_as_paid.short_description = "Mark selected orders as paid"

# custom_admin_site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Product)
admin.site.register(OrderDetail)

