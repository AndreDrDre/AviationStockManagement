# Generated by Django 3.1.7 on 2021-04-28 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0040_auto_20210428_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parts',
            name='recieve_part',
            field=models.BooleanField(default='False'),
        ),
    ]