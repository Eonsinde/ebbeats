import django_filters
from ebbeats.models import *


# write filters for your application here

class ProductFilter(django_filters.FilterSet):
    price = django_filters.NumberFilter(field_name='price')
    genre__name = django_filters.CharFilter(field_name='genre', lookup_expr='exact')
    album__name = django_filters.CharFilter(field_name='album', lookup_expr='iexact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')

    class Meta:
        model = Product
        exclude = ['name', 'file', 'sample', 'duration', 'release_date']
