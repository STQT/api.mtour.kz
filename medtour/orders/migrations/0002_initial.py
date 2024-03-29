# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tournumbers', '0002_initial'),
        ('tourpackages', '0002_tourpackages_tour'),
        ('tours', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecartservices',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_count_services', to='tours.tourpaidservices', verbose_name='Платная услуга корзины'),
        ),
        migrations.AddField(
            model_name='servicecartservices',
            name='service_cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_count_services', to='orders.servicecart', verbose_name='Корзина тура'),
        ),
        migrations.AddField(
            model_name='servicecartpackages',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_count_packages', to='tourpackages.tourpackages', verbose_name='Платная услуга корзины'),
        ),
        migrations.AddField(
            model_name='servicecartpackages',
            name='service_cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_count_packages', to='orders.servicecart', verbose_name='Корзина тура'),
        ),
        migrations.AddField(
            model_name='servicecart',
            name='number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournumbers.tournumbers', verbose_name='Номер тура'),
        ),
        migrations.AddField(
            model_name='servicecart',
            name='tour',
            field=models.ForeignKey(help_text='Выбранный тур пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='tours.tour'),
        ),
    ]
