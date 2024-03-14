# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tourpackages', '0001_initial'),
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tourpackages',
            name='tour',
            field=models.ForeignKey(help_text='Указывайте для прикрепления к туру', on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='tours.tour', verbose_name='Тур'),
        ),
    ]
