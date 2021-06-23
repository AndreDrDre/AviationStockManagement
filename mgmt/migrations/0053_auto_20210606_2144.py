# Generated by Django 3.1.7 on 2021-06-06 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0052_reorderitems_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parts',
            name='cert_document',
            field=models.ImageField(blank=True, null=True, upload_to='Cert-Parts', verbose_name='Certification Document'),
        ),
        migrations.AlterField(
            model_name='tools_calibrated',
            name='calibration_certificate',
            field=models.ImageField(blank=True, null=True, upload_to='Cert-Tools', verbose_name='Certification Document'),
        ),
    ]