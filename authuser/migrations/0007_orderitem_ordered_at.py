# Generated by Django 4.1.7 on 2023-04-02 18:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authuser', '0006_pastorder_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='ordered_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
