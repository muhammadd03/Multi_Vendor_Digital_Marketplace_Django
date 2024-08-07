from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index,name='index'),
    path('product/<int:id>',views.detail,name='detail'),
    # path('success/',views.payment_success_view,name='success'),
    # path('failed/',views.payment_failed_view,name='failed'),
    # path('api/checkout-session/<int:id>',views.create_checkout_session,name='api_checkout_session'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('bank-transfer/<int:product_id>/', views.bank_transfer, name='bank_transfer'),
    path('payment-confirmation/<int:order_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('order-success/', views.order_success, name='order_success'),
    # path('admin/verify-payments/', views.verify_payments, name='verify_payments'),
    path('createproduct/',views.create_product,name='createproduct'),
    path('editproduct/<int:id>/',views.product_edit,name='editproduct'),
    path('delete/<int:id>/',views.product_delete,name='delete'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('register/',views.register,name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='myapp/login.html'),name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('invalid',views.invalid,name='invalid'),
    path('purchases/',views.my_purchases,name='purchases'),
    path('sales/',views.sales,name='sales'),
]