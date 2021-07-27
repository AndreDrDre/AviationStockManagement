# Generated by Django 3.1.7 on 2021-07-27 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0044_auto_20210726_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='tools_uncalibrated',
            name='issuedby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mgmt.employees', verbose_name='Issued By:'),
        ),
        migrations.AddField(
            model_name='tools_uncalibrated',
            name='jobcard',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
