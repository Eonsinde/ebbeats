# Generated by Django 2.1.4 on 2019-12-11 23:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ebbeats', '0014_orderitem_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='user',
        ),
    ]
