# Generated by Django 3.2.15 on 2023-03-05 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournumbers', '0004_alter_numbercabinets_tour_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='numbercabinets',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tournumbers',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
