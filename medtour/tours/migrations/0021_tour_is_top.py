# Generated by Django 3.2.15 on 2023-06-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0020_tour_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='is_top',
            field=models.BooleanField(default=False, verbose_name='Хиты продаж?'),
        ),
    ]
