from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from django.conf import settings
from decimal import Decimal

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album_cover = models.ImageField(upload_to='album_cover/', null=True, blank=True)
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
        if self.discount_price == 0:
            # implies no discount on certain product
            return self.price
        else:
            # implies there is a discount
            return self.discount_price * self.price

    class Meta:
        ordering = ['-release_date']
        permissions = (("can_download_product", "Product can be downloaded"), )


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
    transaction_ref = models.CharField(default='', max_length=100,
                                       help_text="This is auto filled after an "
                                                 "order's state is set to `True` i.e is ordered")

    def __str__(self):
        return f'order {self.id}'

    def set_transaction_ref(self, value):
        if self.ordered:
            self.transaction_ref = value


class Purchase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f'{self.id} Purchase Record'

    class Meta:
        verbose_name = 'Purchase Record'


# other details for the user model
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_picture = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    cover_picture = models.ImageField(upload_to='cover_images/', null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' related images'

    class Meta:
        verbose_name = 'User\'s Profile'


class FAQ(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField(max_length=1500)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

