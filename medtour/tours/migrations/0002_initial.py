# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tours', to='users.organizationcategory', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='tour',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tour_cities', to='users.city', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='tour',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tour_countries', to='users.country', verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='tour',
            name='medical_profiles',
            field=models.ManyToManyField(blank=True, related_name='tours', to='tours.TourMedicalProfile'),
        ),
        migrations.AddField(
            model_name='tour',
            name='org',
            field=models.ForeignKey(help_text='Прикрепленная организация к туру', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tours', to='users.organization', verbose_name='Организация'),
        ),
        migrations.AddField(
            model_name='tour',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tour_regions', to='users.region', verbose_name='Регион'),
        ),
        migrations.AddField(
            model_name='commenttour',
            name='tour',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tours.tour'),
        ),
        migrations.AddField(
            model_name='commenttour',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='additionaltitles',
            name='tour',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tour_titles', to='tours.tour'),
        ),
        migrations.AddField(
            model_name='additionalinfoservices',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_services', to='tours.touradditionaltitle'),
        ),
    ]