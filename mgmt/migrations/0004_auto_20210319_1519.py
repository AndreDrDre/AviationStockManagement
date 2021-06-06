# Generated by Django 3.1.7 on 2021-03-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mgmt', '0003_orderedpart_recieve_part'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockfromshop',
            old_name='issue_by',
            new_name='inspector',
        ),
        migrations.RenameField(
            model_name='stockfromshop',
            old_name='issue_to',
            new_name='vendor',
        ),
        migrations.RemoveField(
            model_name='stockfromshop',
            name='last_updated',
        ),
        migrations.AlterField(
            model_name='stockfromshop',
            name='part_type',
            field=models.CharField(choices=[('Rotable', 'Rotable'), ('Tires', 'Tires'), ('AGS', 'AGS'), ('Shelflife', 'Shelflife'), ('Consumables', 'Consumables'), ('N/A', 'N/A')], default='Rotable', max_length=20),
        ),
    ]
