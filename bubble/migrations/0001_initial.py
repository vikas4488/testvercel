# Generated by Django 5.0.4 on 2024-05-22 07:21

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'aa_category',
            },
        ),
        migrations.CreateModel(
            name='Flowers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('imagetitle', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='flowerimages')),
                ('details', models.CharField(max_length=400)),
                ('price', models.IntegerField()),
                ('offvalue', models.FloatField()),
                ('subcat', models.CharField(default='new plants', max_length=200)),
                ('adddate', models.DateField(blank=True, default=datetime.datetime.now)),
                ('is_active', models.BooleanField(default=True)),
                ('cats', models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='bubble.category')),
            ],
            options={
                'db_table': 'aa_flowers',
            },
        ),
        migrations.CreateModel(
            name='Favorits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adddate', models.DateField(blank=True, default=datetime.datetime.now)),
                ('userob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('flowerob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bubble.flowers')),
            ],
            options={
                'db_table': 'aa_fav',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adddate', models.DateField(blank=True, default=datetime.datetime.now)),
                ('quantity', models.IntegerField(default=1)),
                ('userob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('flowerob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bubble.flowers')),
            ],
            options={
                'db_table': 'aa_cart',
            },
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='bubble.category')),
            ],
            options={
                'db_table': 'aa_subcategory',
            },
        ),
    ]
