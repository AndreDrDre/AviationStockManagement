# Generated by Django 3.1.7 on 2021-07-28 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0045_auto_20210727_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parts',
            name='price',
            field=models.FloatField(blank=True, default='0', null=True),
        ),
    ]
