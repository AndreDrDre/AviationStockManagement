# Generated by Django 3.1.7 on 2021-05-05 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0048_auto_20210505_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='reorderitems',
            name='quantity',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
    ]