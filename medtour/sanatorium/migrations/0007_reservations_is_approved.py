# Generated by Django 3.2.15 on 2023-05-19 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanatorium', '0006_reservations_payment_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservations',
            name='is_approved',
            field=models.BooleanField(default=False, verbose_name='Подтвержден ли клиентом?'),
        ),
    ]