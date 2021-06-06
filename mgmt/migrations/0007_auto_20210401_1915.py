# Generated by Django 3.1.7 on 2021-04-01 19:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0006_auto_20210325_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='parts',
            name='reorder_level',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
        migrations.AlterField(
            model_name='parts',
            name='workorders',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mgmt.workorders'),
        ),
    ]
