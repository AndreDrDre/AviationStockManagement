# Generated by Django 3.1.7 on 2021-07-21 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0033_auto_20210721_1406'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppinglist',
            old_name='re_order',
            new_name='re_orderBoolean',
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='re_orderLevel',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
    ]
