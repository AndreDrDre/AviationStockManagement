# Generated by Django 3.1.7 on 2021-07-12 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0020_auto_20210712_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorders',
            name='date_added',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='workorders',
            name='date_closed',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
