from django.shortcuts import render,redirect
# request, reverse
from django.shortcuts import get_object_or_404
from .models import Product, OrderDetail, UserProfile, Review
# from django.http import JsonResponse
# from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
from .forms import ProductForm, UserRegistrationForm, CheckoutForm
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
import datetime

# Create your views here.
def index(request):
    is_vendor = False
    if request.user.is_authenticated:
        try:
            is_vendor = request.user.profile.is_vendor
        except Exception:
            is_vendor = False
    return render(request, 'myapp/index.html', {'is_vendor': is_vendor})

def products_page(request):
    from django.db.models import Q
    query = request.GET.get('q', '').strip()
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'myapp/products.html', {'products': products, 'query': query})

def detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = product.reviews.all().order_by('-created_on')
    has_purchased = False
    user_review = None
    if request.user.is_authenticated:
        has_purchased = OrderDetail.objects.filter(
            customer_email=request.user.email,
            product=product,
            has_paid=True
        ).exists()
        user_review = Review.objects.filter(product=product, customer=request.user).first()
    if request.method == 'POST' and has_purchased and not user_review:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(
                product=product,
                customer=request.user,
                rating=int(rating),
                comment=comment
            )
            return redirect('detail', id=id)
    return render(request, 'myapp/detail.html', {
        'product': product,
        'reviews': reviews,
        'has_purchased': has_purchased,
        'user_review': user_review,
    })

@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        checkout_form = CheckoutForm(request.POST)
        if checkout_form.is_valid():
            billing = {
                'full_name': checkout_form.cleaned_data['full_name'],
                'phone_number': checkout_form.cleaned_data['phone_number'],
                'address': checkout_form.cleaned_data['address'],
                'city': checkout_form.cleaned_data['city'],
                'payment_method': checkout_form.cleaned_data['payment_method'],
            }
            request.session['billing'] = billing
            if billing['payment_method'] == 'cod':
                OrderDetail.objects.create(
                    customer_email=request.user.email,
                    product=product,
                    amount=int(product.price),
                    has_paid=False,
                    payment_method='cod',
                    full_name=billing['full_name'],
                    phone_number=billing['phone_number'],
                    address=billing['address'],
                    city=billing['city'],
                )
                return redirect('order_success')
            return redirect('bank_transfer', product_id=product.id)
    else:
        checkout_form = CheckoutForm()
    return render(request, 'myapp/checkout.html', {'product': product, 'checkout_form': checkout_form})

@login_required
def bank_transfer(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        amount = request.POST['amount']
        customer_email = request.user.email
        reciept = request.FILES.get('reciept')
        billing = request.session.get('billing', {})
        order = OrderDetail.objects.create(
            customer_email=customer_email,
            product=product,
            amount=int(float(amount)),
            has_paid=False,
            reciept=reciept,
            full_name=billing.get('full_name', ''),
            phone_number=billing.get('phone_number', ''),
            address=billing.get('address', ''),
            city=billing.get('city', ''),
            payment_method='bank_transfer',
        )
        return redirect('payment_confirmation', order_id=order.id)
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

def auth_page(request):
    login_form = AuthenticationForm()
    register_form = UserRegistrationForm()
    active_tab = request.GET.get('tab', 'login')

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                auth_login(request, login_form.get_user())
                return redirect('index')
            active_tab = 'login'
        elif 'register_submit' in request.POST:
            register_form = UserRegistrationForm(request.POST)
            if register_form.is_valid():
                new_user = register_form.save(commit=False)
                new_user.set_password(register_form.cleaned_data['password'])
                new_user.save()
                role = register_form.cleaned_data.get('role')
                profile, _ = UserProfile.objects.get_or_create(user=new_user)
                profile.is_vendor = (role == 'vendor')
                profile.save()
                auth_login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('index')
            active_tab = 'register'

    return render(request, 'myapp/auth.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_tab': active_tab,
    })

def logout_view(request):
    logout(request)
    return redirect('index')

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