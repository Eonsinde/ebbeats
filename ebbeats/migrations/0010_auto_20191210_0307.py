# Generated by Django 2.1.4 on 2019-12-10 02:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ebbeats', '0009_auto_20191209_1827'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['release_date']},
        ),
    ]
