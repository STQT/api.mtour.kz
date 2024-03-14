# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('applications', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='users.organizationcategory', verbose_name='Тип тура'),
        ),
        migrations.AddField(
            model_name='application',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.region', verbose_name='Регион'),
        ),
    ]