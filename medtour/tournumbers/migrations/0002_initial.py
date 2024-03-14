# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tours', '0001_initial'),
        ('tournumbers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournumbers',
            name='tour',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='numbers', to='tours.tour'),
        ),
        migrations.AddField(
            model_name='numbershots',
            name='tour_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournumbers.tournumbers', verbose_name='Номер'),
        ),
        migrations.AddField(
            model_name='numbercabinets',
            name='tour_number',
            field=models.ForeignKey(help_text='Здесь указывается номер тура', on_delete=django.db.models.deletion.CASCADE, related_name='cabinets', to='tournumbers.tournumbers', verbose_name='Номер'),
        ),
    ]