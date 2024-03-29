# Generated by Django 2.1.4 on 2019-12-28 00:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kevibes', '0002_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_picture', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('cover_picture', models.ImageField(blank=True, null=True, upload_to='cover_images/')),
                ('email_confirmed', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User-related-images',
            },
        ),
        migrations.RemoveField(
            model_name='image',
            name='user',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
