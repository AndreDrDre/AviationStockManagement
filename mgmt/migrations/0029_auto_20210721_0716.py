# Generated by Django 3.1.7 on 2021-07-21 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0028_shoppinglist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppinglist',
            options={'verbose_name': 'Shopping List'},
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='order_again',
            field=models.BooleanField(blank=True, default='False', null=True),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='pending',
            field=models.BooleanField(blank=True, default='False', null=True),
        ),
    ]