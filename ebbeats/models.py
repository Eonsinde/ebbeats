from django.db import models
from django.utils import timezone
import datetime
from django.conf import settings
from decimal import Decimal
from django.core.files.storage import FileSystemStorage

# payment imports
from payments import PurchasedItem
from payments.models import BasePayment

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album_cover = models.ImageField(upload_to='album_cover/')
    pub_date = models.DateField(auto_now=timezone.now)

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=500)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f'{self.name}: {self.message[:10]}...'


class Rating(models.Model):
    value = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    def __str__(self):
        return self.user + ' ' + self.value


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True, default=Decimal(1),
                                       help_text="Enter discount in decimal format; e.g 25/100 = .25")
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    duration = models.DurationField(default=timezone.now)
    release_date = models.DateField(auto_created=True)
    TYPE = (
        ('b', 'Beats'),
        ('dk', 'Drum Kits')
    )
    category = models.CharField(default='b', choices=TYPE, max_length=10)
    sample = models.FileField(upload_to='music_previews/', default='', help_text="NB: upload samples for previewing")
    file = models.FileField(upload_to='music_files/')

    def __str__(self):
        return self.name

    def get_recently_released(self):
        return self.release_date >= timezone.now().date() - datetime.timedelta(days=7)

    def get_actual_price(self):
        return self.discount_price * self.price

    class Meta:
        ordering = ['-release_date']


class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return 'Ordered Item {}: {}'.format(str(self.id), self.item.name)

    def get_total_item_price(self):
        return self.item.price

    def get_total_discount_price(self):
        return self.item.price * self.item.discount_price


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default='')
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'order {self.id}'


# other details for the user model
class Image(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='cover_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username + ' related images'

    class Meta:
        verbose_name = 'User-related-images'


# for the payment system of our application
class Payment(BasePayment):
    def get_failure_url(self):
        return 'http://example.com/failure'

    def get_success_url(self):
        return 'http://example.com/success'

    def get_purchased_items(self):
        yield PurchasedItem(name='hounds of justice', sku='BSKU', quantity=9, price=Decimal(9), currency='USD')


