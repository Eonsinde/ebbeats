from django.urls import path
from ebbeats import views

# write your routes here

app_name='ebbeats'

urlpatterns = [
    path('', views.index, name='home'),
    path('explore/', views.explore, name='explore'),
    # path('explore-test/<str:param>/', views.explore_test, name='ex-test'),
    path('album-detail/<int:id>/', views.album_detail, name='album-detail'),
    path('contribute/', views.contribute, name='contribute'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('forms/', views.forms, name='forms'),
    path('login/', views.login_view, name='login-view'),
    path('signup/', views.signup, name='signup-view'),
    path('logout/', views.logout_view, name='logout-view'),
    path('error/', views.error, name='error'),
    path('test-payment/', views.create_and_post,name='test-pay'),
    path('make-payments/<int:payment_id>', views.payment_details, name='payment-details')
]