# Generated by Django 3.1.7 on 2021-07-21 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0031_shoppinglist_part_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='order_quantity',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
    ]
