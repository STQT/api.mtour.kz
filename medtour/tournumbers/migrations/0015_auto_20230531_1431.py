# Generated by Django 3.2.15 on 2023-05-31 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournumbers', '0014_tournumbers_holiday_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournumbers',
            name='type',
        ),
        migrations.DeleteModel(
            name='TourNumberType',
        ),
    ]
