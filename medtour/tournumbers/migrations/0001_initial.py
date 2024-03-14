# Generated by Django 3.2.15 on 2024-03-14 19:49

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import medtour.tournumbers.instances
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NumberCabinets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, help_text='Отметьте, если удалён тур', verbose_name='Удалён?')),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('number', models.IntegerField(help_text='Номер кабинета пакета, присвоится автоматически, при создании пакета', verbose_name='Порядковый номер')),
                ('humanize_name', models.CharField(blank=True, default=None, help_text='Наименование номера кабинета вручную', max_length=30, null=True, verbose_name='Название кабинета')),
            ],
            options={
                'verbose_name': 'Кабинет номера тура',
                'verbose_name_plural': 'Кабинеты номера тура',
                'ordering': ('number',),
            },
        ),
        migrations.CreateModel(
            name='NumberComfort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название комфорта')),
                ('icon', models.FileField(upload_to='number_icons', verbose_name='Файл иконки')),
            ],
            options={
                'verbose_name': 'Название удобства номера',
                'verbose_name_plural': 'Название удобств номера',
            },
        ),
        migrations.CreateModel(
            name='NumberShots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('photo', sorl.thumbnail.fields.ImageField(upload_to=medtour.tournumbers.instances.get_shots_path, verbose_name='Изображение')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Имя изображения')),
            ],
            options={
                'verbose_name': 'Изображение номера',
                'verbose_name_plural': 'Изображения номера',
            },
        ),
        migrations.CreateModel(
            name='TourNumbers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('is_deleted', models.BooleanField(default=False, help_text='Отметьте, если удалён тур', verbose_name='Удалён?')),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('title', models.CharField(default='1 местн. номера', max_length=1000)),
                ('place_count', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('price', models.IntegerField(verbose_name='Цена')),
                ('holiday_price', models.IntegerField(blank=True, null=True, verbose_name='Цена выходного дня')),
                ('capacity', models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='Вместимость')),
                ('max_capacity', models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)], verbose_name='Макс. Вместимость')),
                ('extra_capacity_price', models.IntegerField(default=0, verbose_name='Цена за доп. место')),
                ('hide', models.BooleanField(default=False, verbose_name='Скрыть')),
                ('remarks', models.CharField(blank=True, default='Примечание', max_length=1000, null=True, verbose_name='Примечание')),
                ('comforts', models.ManyToManyField(blank=True, related_name='numbers', to='tournumbers.NumberComfort', verbose_name='Удобства')),
            ],
            options={
                'verbose_name': '* Номер тура',
                'verbose_name_plural': '* Номера туров',
            },
        ),
        migrations.CreateModel(
            name='TourNumbersServices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('title', models.CharField(max_length=1000, verbose_name='Услуга включенного номера')),
                ('hide', models.BooleanField(default=False, verbose_name='Скрыть')),
                ('tour_number', models.ForeignKey(help_text='Укажите конретный номер тура', on_delete=django.db.models.deletion.CASCADE, related_name='number_services', to='tournumbers.tournumbers', verbose_name='Номера туров')),
            ],
            options={
                'verbose_name': 'Услуга номера',
                'verbose_name_plural': 'Услуги номера',
            },
        ),
    ]
