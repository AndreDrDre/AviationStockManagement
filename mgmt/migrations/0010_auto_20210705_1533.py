# Generated by Django 3.1.7 on 2021-07-05 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0009_auto_20210705_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workorders',
            name='type_airframe',
        ),
        migrations.AddField(
            model_name='tailnumber',
            name='serialno',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='tailnumber',
            name='type_airframe',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
