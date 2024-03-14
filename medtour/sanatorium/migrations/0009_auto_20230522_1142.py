# Generated by Django 3.2.15 on 2023-05-22 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanatorium', '0008_alter_reservations_payment_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservations',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='reservations',
            name='approved_status',
            field=models.SmallIntegerField(choices=[(-1, 'Сообщение не отправлено'), (0, 'Сообщение не отправлено'), (1, 'Сообщение не отправлено')], default=-1, verbose_name='Статус подтверждения'),
        ),
    ]
