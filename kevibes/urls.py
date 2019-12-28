from django.urls import path, re_path
from kevibes import views
from django.contrib import admin

# write your routes here

app_name = 'kevibes'

admin.site.site_header = "Kevibes Admin"
admin.site.site_title = "Kevibes Admin Portal"
admin.site.index_title = "Welcome to Kevibes Admin Portal"

urlpatterns = [
    path('', views.index, name='home'),
    path('explore/', views.explore, name='explore'),
    path('album-detail/<int:id>/', views.album_detail, name='album-detail'),
    path('contribute/', views.contribute, name='contribute'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-successful/', views.payment_success, name='payment-successful'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('verify-account/', views.verify_account, name='verify-account'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('forms/', views.forms, name='forms'),
    path('login/', views.login_view, name='login-view'),
    path('signup/', views.signup, name='signup-view'),
    path('logout/', views.logout_view, name='logout-view'),
    path('error/', views.error, name='error'),
]