# Generated by Django 3.1.7 on 2021-04-02 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0011_auto_20210402_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tools_uncalibrated',
            name='recieved',
            field=models.DateTimeField(auto_now=True),
        ),
    ]