# Generated by Django 3.1.7 on 2021-07-08 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0017_auto_20210708_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parts',
            name='breadth',
        ),
        migrations.RemoveField(
            model_name='parts',
            name='height',
        ),
        migrations.RemoveField(
            model_name='parts',
            name='length',
        ),
        migrations.RemoveField(
            model_name='parts',
            name='weight',
        ),
    ]
