# Generated by Django 3.1.7 on 2021-07-07 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0012_auto_20210707_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parts',
            name='repaired_by',
            field=models.CharField(choices=[('INHOUSE REPAIR', 'INHOUSE REPAIR'), (
                'SEND TO SUPPLIER', 'SEND TO SUPPLIER')], default='', max_length=20),
        ),
    ]
