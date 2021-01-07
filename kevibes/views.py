from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.views import generic
from kevibes.models import *
from django.core.paginator import Paginator
from django.core.mail import send_mail
import smtplib
from kevibes.filters import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from kevibes.tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode


# Create your views here.


def index(request):
    context = {
        'products': Product.objects.all()
    }
    return render(request, 'kevibes/index.html', context)


def explore(request):
    products = Product.objects.all()
    albums = Album.objects.all()
    genres = Genre.objects.all()
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_list = paginator.get_page(page)
    if request.method == 'GET' and request.GET.get('query'):
        query = request.GET.get('query')
        query_results = products.filter(name__icontains=f'{query}')
        if query_results:
            paginator = Paginator(query_results, 6)
            page = request.GET.get('page')
            products_list = paginator.get_page(page)
            context = {'products': products_list, 'albums': albums, 'genres': genres}
            return render(request, 'kevibes/explore.html', context)
        else:
            context = {'products': products_list, 'albums': albums, 'genres': genres, 'res_msg': "search result not found"}
            return render(request, 'kevibes/explore.html', context)
    elif request.method == 'GET' and (request.GET.get('album') or request.GET.get('category') or request.GET.get('genre') or request.GET.get('price')):
        f = ProductFilter(request.GET, queryset=products)
        if f.qs.exists():
            paginator = Paginator(f.qs, 6)
            page = request.GET.get('page')
            products_list = paginator.get_page(page)
            context = {'products': products_list, 'albums': albums, 'genres': genres}
            return render(request, 'kevibes/explore.html', context)
        else:
            context = {'products': products_list, 'albums': albums, 'genres': genres, 'res_msg': "No match found for filters"}
            return render(request, 'kevibes/explore.html', context)
    else:
        context = {'products': products_list, 'albums': albums, 'genres': genres}
        return render(request, 'kevibes/explore.html', context)


def album_detail(request, id):
    try:
        found_album = Album.objects.get(id=id)
    except Album.DoesNotExist:
        return HttpResponseRedirect('/error/')
    return render(request, 'kevibes/album-detail.html', {'album': found_album})


def contribute(request):
    return render(request, 'kevibes/forms/contribute.html')


def contact(request):
    if request.method == 'POST':
        new_contact = Contact(name=request.POST['person_name'], email=request.POST['email'],
                              subject=request.POST['subject'], message=request.POST['message'])
        new_contact.save()
        try:
            send_mail(new_contact.subject, new_contact.message, 'olasinde.eon@gmail.com',
                      ['olasinde.eon@gmail.com'], fail_silently=True)
        except smtplib.SMTPException:
            return JsonResponse({'response': 'failure'})
        else:
            return JsonResponse({'response': 'success'})
    else:  # get request
        return render(request, 'kevibes/forms/contact.html')


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'kevibes/dashboard.html')
    else:
        return HttpResponseRedirect('/forms/')


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
                my_file = request.FILES.get('profile-image')
                if user.profile.display_picture:
                    user.profile.display_picture.delete()
                    user.profile.display_picture = my_file
                else:
                    user.profile.display_picture = my_file
                user.profile.save()
            if request.FILES.get('cover-image'):
                my_file = request.FILES.get('cover-image')
                if user.profile.cover_picture:
                    user.profile.cover_picture.delete()
                    user.profile.cover_picture = my_file
                else:
                    user.profile.cover_picture = my_file
                user.profile.save()
            user.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request, 'kevibes/forms/update_profile.html')


def faqs(request):
    return render(request, "kevibes/faqs.html", context={'questions': FAQ.objects.all()})


@login_required
def cart(request):
    order = Order.objects.filter(user=request.user, ordered=False)
    if order.exists():
        return render(request, 'kevibes/cart.html', {'cart': order[0]})
    else:
        return render(request, 'kevibes/cart.html')


def add_to_cart(request, pk):
    if request.user.is_authenticated:
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
                order.save()
                return JsonResponse({'message': 'success'})
    else:
        return JsonResponse({"message": 'failure'})


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
                order.save()
                return JsonResponse({'message': 'removed'})
            else:  # if not; do nothing
                return JsonResponse({'message': 'not_present'})
        else:
            return JsonResponse({'message': 'no_order'})


@login_required
def checkout(request):
    order = Order.objects.get(user=request.user, ordered=False)
    context = {
        'cart': order.items.all()
    }
    return render(request, 'kevibes/checkout.html', context)


def payment_success(request):
    response = request.POST.get('message')
    if response == 'success':
        order = Order.objects.get(user=request.user, ordered=False)
        order.ordered = True
        order.set_transaction_ref(request.POST.get('transaction_ref'))
        order.save()

        # continue from here 
        purchase_record = Purchase.objects.create(user=request.user)
        

        order_id = order.id
        # to change it's permissions
        permission = Permission.objects.get(codename='can_download_product')
        user = User.objects.get(user=request.user)
        user.user_permissions.set(permission)
        user.save()
        return redirect('kevibes:download-products', id=order_id)


# @permission_required('kevibes.can_download_product')
@login_required
def download_products(request, order_id):
    if request.method == 'GET':
        order = get_object_or_404(Order, pk=order_id)
        # permission = Permission.objects.get(codename='can_download_product')
        return render(request, 'kevibes/download_products.html', context={'order': order})


def forms(request):
    if request.method == "GET":
        return render(request, 'kevibes/forms/forms.html')


def signup(request):
    if request.method == 'POST':
        if request.POST is not None:
            new_user = User()
            new_user.username = request.POST['username']
            new_user.email = request.POST['email']
            new_user.set_password(request.POST['password'])
            new_user.save()
            new_prof_instance = Profile.objects.create(user=new_user, display_picture='', cover_picture='')
            new_prof_instance.save()
            return render(request, 'kevibes/forms/forms.html', {'message': 'Account successfully created; login'})
        else:
            return render(request, 'kevibes/forms/forms.html', {'message': "Validation Error; check that all fields are filled"})
    else:
        return HttpResponseRedirect('/kevibes/forms/')


def verify_account(request):
    current_site = get_current_site(request)
    subject = 'Activate Your Kevibes Account'
    context = {
        'user': request.user,
        'domain': "localhost:8000",
        'uid': urlsafe_base64_encode(force_bytes(request.user.pk)).decode(),
        'token': account_activation_token.make_token(request.user)
    }
    print(current_site)
    print("UID:", context['uid'])

    message = render_to_string('kevibes/acc/account_activation_email.html', context)
    try:
        request.user.email_user(subject, message)
    except smtplib.SMTPException:
        return JsonResponse({'message': 'Oops! Try Again'})
    return JsonResponse({'message': 'Account Verification Sent'})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.profile.email_confirmed = True
        user.profile.save()
        user.save()
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponse("Error in account verification -- activation link not valid")


def login_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        else:
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            nextValue = request.POST.get('next-value')
            print(nextValue)
            if user is not None and (nextValue == '' or nextValue == None): # if no next value 
                login(request, user)
                return HttpResponseRedirect('/')
            elif user is not None and nextValue: # to ensure a user is properly redirected
                login(request, user)
                return HttpResponseRedirect(nextValue)
            else:
                return render(request, 'kevibes/forms/forms.html', {'message': 'invalid login credentials'})
    else: # get request
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return render(request, 'kevibes/forms/forms.html')


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/forms/')


def handler403(request, exception, template_name='kevibes/error_page.html'):
    pass


def handler404(request, exception, template_name='kevibes/error_page.html'):
    return HttpResponseBadRequest()








