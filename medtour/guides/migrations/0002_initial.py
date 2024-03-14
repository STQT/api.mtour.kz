# Generated by Django 3.2.15 on 2024-03-14 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('guides', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='guidereview',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guide_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='guideprogram',
            name='guide',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='guides.guide'),
        ),
        migrations.AddField(
            model_name='guideprogram',
            name='services',
            field=models.ManyToManyField(blank=True, to='guides.GuideServices', verbose_name='Включенные услуги'),
        ),
        migrations.AddField(
            model_name='guide',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guides', to='guides.guidecategory', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='guide',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guide_cities', to='users.city', verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='guide',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guide_countries', to='users.country', verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='guide',
            name='org',
            field=models.OneToOneField(help_text='Прикрепленная организация к гиду', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guides', to='users.organization', verbose_name='Организация'),
        ),
        migrations.AddField(
            model_name='guide',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guide_regions', to='users.region', verbose_name='Регион'),
        ),
    ]
