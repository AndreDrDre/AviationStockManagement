# Generated by Django 3.1.7 on 2021-06-24 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0004_auto_20210624_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderhistory',
            name='ordered_by',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='part_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='tail_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
