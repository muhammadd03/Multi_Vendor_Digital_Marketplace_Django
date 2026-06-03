from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products_page, name='products'),
    path('product/<int:id>', views.detail, name='detail'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('bank-transfer/<int:product_id>/', views.bank_transfer, name='bank_transfer'),
    path('payment-confirmation/<int:order_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('order-success/', views.order_success, name='order_success'),
    path('createproduct/', views.create_product, name='createproduct'),
    path('editproduct/<int:id>/', views.product_edit, name='editproduct'),
    path('delete/<int:id>/', views.product_delete, name='delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('auth/', views.auth_page, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('invalid', views.invalid, name='invalid'),
    path('purchases/', views.my_purchases, name='purchases'),
    path('sales/', views.sales, name='sales'),
]
