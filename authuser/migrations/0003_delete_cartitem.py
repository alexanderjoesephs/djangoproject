# Generated by Django 4.1.7 on 2023-03-29 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authuser', '0002_cart_product_cartitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
