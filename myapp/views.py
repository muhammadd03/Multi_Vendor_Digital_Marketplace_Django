from django.shortcuts import render,redirect
# request, reverse
from django.shortcuts import get_object_or_404
from .models import Product,OrderDetail
# from django.http import JsonResponse
# from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
from .forms import ProductForm, UserRegistrationForm
from django.contrib.auth import logout
from django.db.models import Sum
import datetime

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, 'myapp/index.html',{'products':products})

def detail(request,id):
    product = Product.objects.get(id=id)
    return render(request,'myapp/detail.html',{'product':product})

@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        return redirect('bank_transfer', product_id=product.id)
    return render(request, 'myapp/checkout.html', {'product': product})

@login_required
def bank_transfer(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        amount = request.POST['amount']
        customer_email = request.user.email
        reciept = request.FILES.get('reciept') 
        order = OrderDetail.objects.create(
            customer_email=customer_email,
            product=product,
            amount=amount,
            has_paid=False,
            reciept=reciept
        )
        return redirect('payment_confirmation',order_id = order.id)
    return render(request, 'myapp/bank_transfer.html', {'product': product})

@login_required
def payment_confirmation(request, order_id):
     order = get_object_or_404(OrderDetail, id=order_id)
     product = order.product
     if request.method == 'POST':
        order.has_paid=True
        order.save()
        #updating sales stats for a product
        product.total_sales_amount += order.amount
        product.total_sales += 1
        product.save()
        #updating sales stats for a product
        return redirect('order_success')
     return render(request, 'myapp/payment_confirmation.html', {'order': order})

@login_required
def order_success(request):
    return render(request, 'myapp/order_success.html')

def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            new_product = product_form.save(commit=False)
            new_product.seller = request.user
            new_product.save()
            return redirect('index')
    product_form = ProductForm()

    return render (request, 'myapp/create_product.html',{'product_form':product_form})

def product_edit(request,id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    
    product_form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST':
        if product_form.is_valid():
            product_form.save()
            return redirect('index')
    return render(request,'myapp/product_edit.html',{'product_form':product_form, 'product':product})


def product_delete(request,id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect('invalid')
    if request.method == 'POST':
        product.delete()
        return redirect('index')
    return render(request, 'myapp/delete.html',{'product':product})


def dashboard(request):
    products = Product.objects.filter(seller = request.user)
    return render(request,'myapp/dashboard.html',{'products':products})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        new_user = user_form.save(commit=False)
        new_user.set_password(user_form.cleaned_data['password'])
        new_user.save()
        return redirect('index')
    user_form = UserRegistrationForm()
    return render(request, 'myapp/register.html',{'user_form':user_form})

def logout_view(request):
    logout(request)
    return render(request,'myapp/logout.html')

def sales(request):
    orders = OrderDetail.objects.filter(product__seller=request.user)
    total_sales =  orders.aggregate(Sum('amount'))

    #365 day sales sum
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_year)
    yearly_sales = data.aggregate(Sum('amount'))
    #30 day sales sum
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    data = OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_month)
    monthly_sales = data.aggregate(Sum('amount'))
    #7 day sales sum
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    data = OrderDetail.objects.filter(product__seller=request.user,created_on__gt=last_week)
    weekly_sales = data.aggregate(Sum('amount'))

    #Everyday sum for the past 30 days
    daily_sales_sums = OrderDetail.objects.filter(product__seller=request.user).values('created_on__date').order_by('created_on__date').annotate(sum=Sum('amount'))


    #Product Sale sum
    product_sales_sums = OrderDetail.objects.filter(product__seller=request.user).values('product__name').order_by('product__name').annotate(sum=Sum('amount'))

    return render(request, 'myapp/sales.html',{'total_sales':total_sales, 'yearly_sales':yearly_sales,'monthly_sales':monthly_sales,'weekly_sales':weekly_sales,'daily_sales_sums':daily_sales_sums,'product_sales_sums':product_sales_sums})

# def is_admin(user):
#     return user.is_superuser

# @user_passes_test(is_admin)
# def verify_payments(request):
#     if request.method == 'POST':
#         order_id = request.POST['order_id']
#         order = get_object_or_404(OrderDetail, id=order_id)
#         order.has_paid = True
#         order.save()
#         # Optionally, send a confirmation email to the customer
#     pending_orders = OrderDetail.objects.filter(has_paid=False)
#     return render(request, 'myapp/verify_payment.html', {'pending_orders': pending_orders})


# @csrf_exempt
# def create_checkout_session(request,id):
#     request_data = json.loads(request.body)
#     product = Product.objects.get(id=id)
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     checkout_session = stripe.checkout.Session.create(
#         customer_email = request_data['data'],
#         payment_method_types = ['card'],
#         line_items = [
#             {
#                 'price_data':{
#                     'currency':'usd',
#                     'product_data':{
#                         'name':product.name,
#                     },
#                     'unit_amount':int(product.price * 100),
#                 },
#                 'quantity':1,
#             }
#         ],
#         mode = 'payment',
#         success_url = request.build_absolute_uri(reverse('success')) +
#         "?session_id={CHECKOUT_SESSION_ID}",
#         cancel_url = request.build_absolute_uri(reverse('failed'))
#     )



#order = OrderDetail()
#user = request.user
#order.customer_email = request_data['email']
#order.product = product
# order.stripe_payment_intent = checkout_session['payment_intent']
# order.amount = int(product.price)
# order.save()
# return JsonResponse({'sessionId':checkout_session.id})

# def payment_success_view(request):
#     session_id = request.GET.get('session_id')
#     if session_id is None:
#         return HttpResponseNotFound()
#     # stripe.api_key = settings.STRIPE_SECRET_KEY
#     session = stripe.checkout.Session.retrieve(session_id)
#     order = get_object_or_404(OrderDetail,stripe_payment_intent=session.payment_intent)
#     order.has_paid=True
#     order.save()
#     return render(request,'myapp/payment_success.html',{'order':order})

# def payment_failed_view(request):
#     return render(request,'myapp/failed.html')

def invalid(request):
    return render(request, 'myapp/invalid.html')

def my_purchases(request):
    orders = OrderDetail.objects.filter(customer_email=request.user.email)
    return render(request, 'myapp/purchases.html',{'orders':orders})