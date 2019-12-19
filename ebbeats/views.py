from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import generic
from ebbeats.models import *
from django.core.paginator import Paginator
from django.core.mail import send_mail
import smtplib
from ebbeats.filters import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

# payment thingy
from payments import get_payment_model, RedirectNeeded


# Create your views here.


def index(request):
    context = {
        'products': Product.objects.all()
    }
    return render(request, 'ebbeats/index.html', context)


def explore(request):
    if request.method == 'GET':
        products = Product.objects.all()
        albums = Album.objects.all()
        genres = Genre.objects.all()
        if request.GET.get('query'):
            query = request.GET.get('query')
            products = products.filter(name__icontains=f'{query}')
            print('Search: ', products)
            paginator = Paginator(products, 1)
            page = request.GET.get('page')
            products_list = paginator.get_page(page)
            context = {'products': products_list, 'albums': albums, 'genres': genres}
            return render(request, 'ebbeats/explore.html', context)
        elif request.GET.get('album') or request.GET.get('category') or request.GET.get('genre') or request.GET.get('price'):
            print(products)
            f = ProductFilter(request.GET, queryset=products)
            print('filtering')
            print(f.qs)
            paginator = Paginator(f.qs, 1)
            page = request.GET.get('page')
            products_list = paginator.get_page(page)
            context = {'products': products_list, 'albums': albums, 'genres': genres}
            return render(request, 'ebbeats/explore.html', context)
        else:
            paginator = Paginator(products, 9)
            page = request.GET.get('page')
            products_list = paginator.get_page(page)
            context = {'products': products_list, 'albums': albums, 'genres': genres}
            return render(request, 'ebbeats/explore.html', context)


def album_detail(request, id):
    try:
        found_album = Album.objects.get(id=id)
    except Album.DoesNotExist:
        return HttpResponseRedirect('/ebbeats/error/')
    return render(request, 'ebbeats/album-detail.html', {'album': found_album})


def contribute(request):
    return render(request, 'ebbeats/forms/contribute.html')

#
# def search(request):
#     query = request.GET['query']
#     products = Product.objects.filter(name__icontains=f'{query}')
#     # page_obj = Paginator(products, 1)
#     return render(request, 'ebbeats/search.html', context={'products': products})
#
#
# def filter_(request):
#     if request.method == 'GET':
#         f = ProductFilter(request.GET, queryset=Product.objects.all())
#         return render(request, 'ebbeats/filter.html', {'filter': f})


def contact(request):
    if request.method == 'POST':
        new_contact = Contact(name=request.POST['person_name'], email=request.POST['email'],
                              subject=request.POST['subject'], message=request.POST['message'])
        new_contact.save()
        try:
            send_mail(new_contact.subject, new_contact.message, 'olasinde.eon@gmail.com',
                      [new_contact.email], fail_silently=True)
        except smtplib.SMTPException:
            return JsonResponse({'response': 'failure'})
        else:
            return JsonResponse({'response': 'success'})
    else:  # get request
        return render(request, 'ebbeats/forms/contact.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'ebbeats/dashboard.html')
    else:
        return HttpResponseRedirect('/ebbeats/forms/')


@login_required
def update_profile(request):
    if request.method == "POST":
        if request.POST:
            user = request.user
            if request.POST['username']:
                user.username = request.POST['username']
            if request.POST['email']:
                user.email = request.POST['email']
            if request.POST['password']:
                user.set_password = request.POST['password']
            if request.FILES.get('profile-image'):
                print(request.FILES.get('profile-image'))
                user.image.profile_image = request.FILES.get('profile-image')
            if request.FILES.get('cover-image'):
                print(request.FILES.get('cover-image'))
                user.image.cover_image = request.FILES.get('cover-image')
            user.save()
            return HttpResponseRedirect('/ebbeats/dashboard/')
    return render(request, 'ebbeats/forms/update_profile.html')


@login_required
def cart(request):
    order = Order.objects.filter(user=request.user, ordered=False)
    if order.exists():
        return render(request, 'ebbeats/cart.html', {'cart': order[0]})
    else:
        return render(request, 'ebbeats/cart.html')


@login_required
def add_to_cart(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'failure'})
    else:
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__pk=product.id).exists():
                return JsonResponse({'message': 'present'})
            else:  # if not in order add it
                order_item = OrderItem.objects.create(item=product, user=request.user)
                order.items.add(order_item)
                return JsonResponse({'message': 'success'})
        else:
            order = Order.objects.create(user=request.user, ordered_date=timezone.now())
            order_item = OrderItem.objects.create(item=product, user=request.user)
            order.items.add(order_item)
            return JsonResponse({'message': 'success'})


@login_required
def remove_from_cart(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'message': 'failure'})
    else:
        # order_item = OrderItem.objects.create(item=product)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__pk=product.id).exists():
                ord_item_to_remove = order.items.get(item__pk=product.id, user=request.user)
                order.items.remove(ord_item_to_remove)
                return JsonResponse({'message': 'removed'})
            else:  # if not; do nothing
                return JsonResponse({'message': 'not_present'})
        else:
            return JsonResponse({'message': 'no_order'})


@login_required
def checkout(request):
    return render(request, 'ebbeats/checkout.html')


def forms(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/ebbeats/')
    else:
        return render(request, 'ebbeats/forms/forms.html')


def signup(request):
    if request.method == 'POST':
        if request.POST is not None:
            new_user = User()
            new_user.username = request.POST['username']
            new_user.email = request.POST['email']
            new_user.set_password(request.POST['password'])
            new_user.save()

            return render(request, 'ebbeats/forms/forms.html', {'message': 'Account successfully created; login'})
        else:
            return render(request, 'ebbeats/forms/forms.html', {'message': "Validation Error; check that all fields are filled"})
    else:
        return HttpResponseRedirect('/ebbeats/forms/')


def login_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/ebbeats/')
        else:
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/ebbeats/')
            else:
                return render(request, 'ebbeats/forms/forms.html', {'message': 'invalid login credentials'})
    else:
        return render(request, 'ebbeats/forms/forms.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/ebbeats/')
    else:
        return HttpResponseRedirect('/ebbeats/forms/')


def error(request):
    return render(request, 'ebbeats/error_page.html')


# for the payment system
def create_and_post(request):
    Payment = get_payment_model()
    payment = Payment.objects.create(
        variant='default',
        description='Book purchase',
        total=Decimal(120),
        tax=Decimal(20),
        currency='USD',
        delivery=Decimal(10),
        billing_first_name='Sherlock',
        billing_last_name='Holmes',
        billing_address_1='221B Baker Street',
        billing_address_2='',
        billing_city='London',
        billing_postcode='NW1 6XE',
        billing_country_code='UK',
        billing_country_area='Greater London',
        customer_ip_address='127.0.0.1'
    )
    payment.save()
    return redirect('ebbeats:payment-details', payment.id)


def payment_details(request, payment_id):
    payment = get_object_or_404(get_payment_model(), id=payment_id)
    try:
        payment_form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    print(payment.token)
    return render(request, 'ebbeats/forms/payment.html', {'payment_form': payment_form, 'payment': payment})






