# Generated by Django 3.1.7 on 2021-07-08 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0018_auto_20210708_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='parts',
            name='breadth',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='parts',
            name='height',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='parts',
            name='length',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='parts',
            name='weight',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
