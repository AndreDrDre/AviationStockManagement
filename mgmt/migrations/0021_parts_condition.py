# Generated by Django 3.1.7 on 2021-04-07 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0020_auto_20210407_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='parts',
            name='condition',
            field=models.CharField(choices=[('OH', 'OH'), ('NEW', 'NEW'), ('SV', 'SV'), ('AR', 'AR'), ('REPAIRABLE', 'REPAIRABLE')], default='NEW', max_length=20),
        ),
    ]
