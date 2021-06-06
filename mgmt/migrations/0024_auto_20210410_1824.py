# Generated by Django 3.1.7 on 2021-04-10 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0023_parts_date_received'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parts',
            name='condition',
            field=models.CharField(choices=[('OH', 'OH'), ('NEW', 'NEW'), ('SV', 'SV'), ('AR', 'AR'), ('MIS-INFO', 'MIS-INFO'), ('REPAIRABLE', 'REPAIRABLE')], default='NEW', max_length=20),
        ),
    ]
