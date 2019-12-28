# Generated by Django 2.1.4 on 2019-12-28 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kevibes', '0003_auto_20191228_0123'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Users Profile'},
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_ref',
            field=models.CharField(default='', help_text="This is auto filled after an order's state is set to `True` i.e is ordered", max_length=100),
        ),
    ]
