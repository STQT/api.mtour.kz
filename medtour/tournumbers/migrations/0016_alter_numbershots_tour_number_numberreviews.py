# Generated by Django 4.1.9 on 2023-06-30 03:49

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tournumbers", "0015_auto_20230531_1431"),
    ]

    operations = [
        migrations.AlterField(
            model_name="numbershots",
            name="tour_number",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="number_shots",
                to="tournumbers.tournumbers",
                verbose_name="Номер",
            ),
        ),
        migrations.CreateModel(
            name="NumberReviews",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "purity",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Чистота",
                    ),
                ),
                (
                    "service",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Сервис",
                    ),
                ),
                (
                    "location",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Местоположение",
                    ),
                ),
                (
                    "staff",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Персонал",
                    ),
                ),
                (
                    "proportion",
                    models.IntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Соотношение цена/качество",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        validators=[
                            django.core.validators.MinLengthValidator(
                                20, message="Минимальная длина отзыва должна превышать 20 символа"
                            )
                        ]
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tour",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="number_reviews",
                        to="tournumbers.tournumbers",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="number_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Отзыв номера",
                "verbose_name_plural": "Отзывы номеров",
                "ordering": ("-created_at",),
            },
        ),
    ]